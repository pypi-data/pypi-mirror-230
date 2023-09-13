from collections import defaultdict
from typing import Union

import torch
from torch.optim.lr_scheduler import StepLR

from scvi.train import TrainingPlan

import numpy as np

from ._module import CPAModule


class CPATrainingPlan(TrainingPlan):
    def __init__(
            self,
            module: CPAModule,
            covars_to_ncovars: dict,
            lr=1e-3,
            wd=1e-6,
            n_steps_kl_warmup: int = 0,
            n_epochs_kl_warmup: int = 0,
            n_epochs_adv_warmup: int = 0,
            n_epochs_mixup_warmup: int = 0,
            mixup_alpha: float = 0.2,
            adv_steps: int = 3,
            reg_adv: float = 1.,
            pen_adv: float = 1.,
            adv_lr=3e-4,
            adv_wd=1e-6,
            doser_lr=1e-4,
            doser_wd=1e-6,
            step_size_lr: int = 45,
    ):
        """Training plan for the CPA model"""
        super().__init__(
            module=module,
            lr=lr,
            weight_decay=wd,
            n_steps_kl_warmup=n_steps_kl_warmup,
            n_epochs_kl_warmup=n_epochs_kl_warmup,
            reduce_lr_on_plateau=False,
            lr_factor=None,
            lr_patience=None,
            lr_threshold=None,
            lr_scheduler_metric=None,
            lr_min=None,
        )

        self.automatic_optimization = False

        self.wd = wd

        self.covars_encoder = covars_to_ncovars

        self.mixup_alpha = mixup_alpha
        self.n_epochs_mixup_warmup = n_epochs_mixup_warmup

        self.n_epochs_adv_warmup = n_epochs_adv_warmup
        self.adv_steps = adv_steps

        self.reg_adv = reg_adv
        self.pen_adv = pen_adv

        self.adv_lr = adv_lr
        self.adv_wd = adv_wd

        self.doser_lr = doser_lr
        self.doser_wd = doser_wd

        self.step_size_lr = step_size_lr

        self.metrics = ['recon_loss', 'KL',
                        'disnt_basal', 'disnt_after',
                        'r2_mean', 'r2_var',
                        'adv_loss', 'penalty_adv', 'adv_perts', 'acc_perts', 'penalty_perts']

        self.epoch_history = defaultdict(list)

        self.iter_count = 0

    def configure_optimizers(self):
        ae_params = list(filter(lambda p: p.requires_grad, self.module.encoder.parameters())) + \
                    list(filter(lambda p: p.requires_grad, self.module.decoder.parameters())) + \
                    list(filter(lambda p: p.requires_grad, self.module.pert_network.pert_embedding.parameters())) + \
                    list(filter(lambda p: p.requires_grad, self.module.covars_embeddings.parameters()))

        if self.module.recon_loss in ['zinb', 'nb']:
            ae_params += list(filter(lambda p: p.requires_grad, self.module.library_encoder.parameters())) + \
                         [self.module.px_r]

        optimizer_autoencoder = torch.optim.Adam(
            ae_params,
            lr=self.lr,
            weight_decay=self.wd)

        scheduler_autoencoder = StepLR(optimizer_autoencoder, step_size=self.step_size_lr)

        doser_params = list(filter(lambda p: p.requires_grad, self.module.pert_network.dosers.parameters()))
        optimizer_doser = torch.optim.Adam(
            doser_params, lr=self.doser_lr, weight_decay=self.doser_wd,
        )
        scheduler_doser = StepLR(optimizer_doser, step_size=self.step_size_lr)

        adv_params = list(filter(lambda p: p.requires_grad, self.module.perturbation_classifier.parameters())) + \
                     list(filter(lambda p: p.requires_grad, self.module.covars_classifiers.parameters()))

        optimizer_adversaries = torch.optim.Adam(
            adv_params,
            lr=self.adv_lr,
            weight_decay=self.adv_wd)
        scheduler_adversaries = StepLR(optimizer_adversaries, step_size=self.step_size_lr)

        optimizers = [optimizer_autoencoder, optimizer_doser, optimizer_adversaries]
        schedulers = [scheduler_autoencoder, scheduler_doser, scheduler_adversaries]

        if self.step_size_lr is not None:
            return optimizers, schedulers
        else:
            return optimizers

    def training_step(self, batch, batch_idx):
        opt, opt_doser, opt_adv = self.optimizers()

        if self.current_epoch < self.n_epochs_mixup_warmup:
            mixup_alpha = 0.0
        else:
            mixup_alpha = self.mixup_alpha

        batch, mixup_lambda = self.module.mixup_data(batch, alpha=mixup_alpha)

        inf_outputs, gen_outputs = self.module.forward(batch, compute_loss=False,
                                                       inference_kwargs={'mixup_lambda': mixup_lambda})

        if self.current_epoch >= self.n_epochs_adv_warmup:
            # Adversarial update
            if batch_idx % self.adv_steps != 0:
                opt_adv.zero_grad()

                z_basal = inf_outputs['z_basal']

                adv_results = self.module.adversarial_loss(tensors=batch, z_basal=z_basal, mixup_lambda=mixup_lambda)

                adv_loss = adv_results['adv_loss'] + self.pen_adv * adv_results['penalty_adv']

                self.manual_backward(adv_loss)

                self.clip_gradients(opt_adv,
                                    gradient_clip_val=1.0,
                                    gradient_clip_algorithm="norm")

                opt_adv.step()

                for key, val in adv_results.items():
                    adv_results[key] = val.item()

                results = adv_results.copy()
                results.update({'recon_loss': 0.0})
                results.update({'KL': 0.0})

            # Model update
            else:
                opt.zero_grad()
                opt_doser.zero_grad()

                recon_loss, kl_loss = self.module.loss(
                    tensors=batch,
                    inference_outputs=inf_outputs,
                    generative_outputs=gen_outputs,
                )
                z_basal = inf_outputs['z_basal']
                adv_results = self.module.adversarial_loss(tensors=batch, z_basal=z_basal, mixup_lambda=mixup_lambda)

                loss = recon_loss + self.kl_weight * kl_loss - self.reg_adv * adv_results['adv_loss']

                self.manual_backward(loss)

                self.clip_gradients(opt,
                                    gradient_clip_val=1.0,
                                    gradient_clip_algorithm="norm")
                self.clip_gradients(opt_doser,
                                    gradient_clip_val=1.0,
                                    gradient_clip_algorithm="norm")
                opt.step()
                opt_doser.step()

                for key, val in adv_results.items():
                    adv_results[key] = val.item()

                results = adv_results.copy()

                results.update({'recon_loss': recon_loss.item()})
                results.update({'KL': kl_loss.item()})

        else:
            adv_results = {'adv_loss': 0.0, 'cycle_loss': 0.0, 'penalty_adv': 0.0,
                           'adv_perts': 0.0, 'acc_perts': 0.0, 'penalty_perts': 0.0}
            for covar in self.covars_encoder.keys():
                adv_results[f'adv_{covar}'] = 0.0
                adv_results[f'acc_{covar}'] = 0.0
                adv_results[f'penalty_{covar}'] = 0.0

            results = adv_results.copy()

            opt.zero_grad()
            opt_doser.zero_grad()

            recon_loss, kl_loss = self.module.loss(
                tensors=batch,
                inference_outputs=inf_outputs,
                generative_outputs=gen_outputs,
            )

            loss = recon_loss + self.kl_weight * kl_loss

            self.manual_backward(loss)

            self.clip_gradients(opt,
                                gradient_clip_val=1.0,
                                gradient_clip_algorithm="norm")
            self.clip_gradients(opt_doser,
                                gradient_clip_val=1.0,
                                gradient_clip_algorithm="norm")

            opt.step()
            opt_doser.step()

            results.update({'recon_loss': recon_loss.item()})
            results.update({'KL': kl_loss.item()})

        self.iter_count += 1

        results.update({'r2_mean': 0.0, 'r2_var': 0.0})
        results.update({'r2_mean_lfc': 0.0, 'r2_var_lfc': 0.0})
        results.update({'cpa_metric': 0.0})
        results.update({'disnt_basal': 0.0, 'disnt_after': 0.0})

        return results

    def training_epoch_end(self, outputs):
        for key in self.metrics:
            if key in ['r2_mean', 'r2_var', 'disnt_basal', 'disnt_after']:
                self.epoch_history[key].append(0.0)
            elif key.startswith('acc_') and self.current_epoch < self.n_epochs_adv_warmup:
                self.epoch_history[key].append(0.0)
            else:
                self.epoch_history[key].append(np.mean([output[key] for output in outputs if output[key] != 0.0]))

        for covar, unique_covars in self.covars_encoder.items():
            if len(unique_covars) > 1:
                key1, key2, key3 = f'adv_{covar}', f'penalty_{covar}', f'acc_{covar}'
                self.epoch_history[key1].append(np.mean([output[key1] for output in outputs if output[key1] != 0.0]))
                self.epoch_history[key2].append(np.mean([output[key2] for output in outputs if output[key2] != 0.0]))
                self.epoch_history[key3].append(np.mean([output[key3] for output in outputs if output[key3] != 0.0]))

        self.epoch_history['epoch'].append(self.current_epoch)
        self.epoch_history['mode'].append('train')

        self.log("recon", self.epoch_history['recon_loss'][-1], prog_bar=True)
        self.log("adv_acc_perts", self.epoch_history['acc_perts'][-1], prog_bar=True)

        if self.current_epoch > 1 and self.iter_count % self.step_size_lr == 0:
            sch, sch_doser, sch_adv = self.lr_schedulers()
            sch.step()
            sch_doser.step()
            sch_adv.step()

    def validation_step(self, batch, batch_idx):
        batch, mixup_lambda = self.module.mixup_data(batch, alpha=1.0)

        inf_outputs, gen_outputs = self.module.forward(batch, compute_loss=False,
                                                       inference_kwargs={
                                                           'mixup_lambda': 1.0,
                                                       })

        recon_loss, kl_loss = self.module.loss(
            tensors=batch,
            inference_outputs=inf_outputs,
            generative_outputs=gen_outputs,
        )

        adv_results = {'adv_loss': 0.0, 'cycle_loss': 0.0, 'penalty_adv': 0.0,
                       'adv_perts': 0.0, 'acc_perts': 0.0, 'penalty_perts': 0.0}
        for covar in self.covars_encoder.keys():
            adv_results[f'adv_{covar}'] = 0.0
            adv_results[f'acc_{covar}'] = 0.0
            adv_results[f'penalty_{covar}'] = 0.0

        r2_mean, r2_var = self.module.r2_metric(batch, inf_outputs, gen_outputs, mode='direct')
        # r2_mean_lfc, r2_var_lfc = self.module.r2_metric(batch, inf_outputs, gen_outputs, mode='lfc')
        disnt_basal, disnt_after = self.module.disentanglement(batch, inf_outputs, gen_outputs)

        results = adv_results
        results.update({'r2_mean': r2_mean.item(), 'r2_var': r2_var.item()})
        results.update({'disnt_basal': disnt_basal})
        results.update({'disnt_after': disnt_after})
        results.update({'KL': kl_loss.item()})
        results.update({'recon_loss': recon_loss.item()})
        results.update({'cpa_metric': r2_mean.item() + 0.5 * r2_var.item() + 1.5 * (disnt_after - disnt_basal)})

        return results

    def validation_epoch_end(self, outputs):
        for key in self.metrics:
            self.epoch_history[key].append(np.mean([output[key] for output in outputs if output[key] != 0.0]))

        for covar, unique_covars in self.covars_encoder.items():
            if len(unique_covars) > 1:
                key1, key2, key3 = f'adv_{covar}', f'penalty_{covar}', f'acc_{covar}'
                self.epoch_history[key1].append(np.mean([output[key1] for output in outputs if output[key1] != 0.0]))
                self.epoch_history[key2].append(np.mean([output[key2] for output in outputs if output[key2] != 0.0]))
                self.epoch_history[key3].append(np.mean([output[key3] for output in outputs if output[key3] != 0.0]))

        self.epoch_history['epoch'].append(self.current_epoch)
        self.epoch_history['mode'].append('valid')

        self.log('val_recon', self.epoch_history['recon_loss'][-1], prog_bar=True)
        self.log('cpa_metric', np.mean([output['cpa_metric'] for output in outputs]), prog_bar=False)
        self.log('disnt_basal', self.epoch_history['disnt_basal'][-1], prog_bar=True)
        self.log('disnt_after', self.epoch_history['disnt_after'][-1], prog_bar=True)
        self.log('val_r2_mean', self.epoch_history['r2_mean'][-1], prog_bar=True)
        self.log('val_r2_var', self.epoch_history['r2_var'][-1], prog_bar=False)
        # self.log('val_r2_mean_lfc', self.epoch_history['r2_mean_lfc'][-1], prog_bar=True)
        # self.log('val_r2_var_lfc', self.epoch_history[
        # 'r2_var_lfc'][-1], prog_bar=False)
        self.log('val_KL', self.epoch_history['KL'][-1], prog_bar=True)

        if self.current_epoch % 20 == 19:
            print(f'\ndisnt_basal = {self.epoch_history["disnt_basal"][-1]}')
            print(f'disnt_after = {self.epoch_history["disnt_after"][-1]}')
            print(f'val_r2_mean = {self.epoch_history["r2_mean"][-1]}')
            print(f'val_r2_var = {self.epoch_history["r2_var"][-1]}')
