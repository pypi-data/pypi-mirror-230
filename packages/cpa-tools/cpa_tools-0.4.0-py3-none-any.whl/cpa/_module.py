import numpy as np
import torch
import torch.nn as nn
from scvi import settings
from scvi.distributions import NegativeBinomial, ZeroInflatedNegativeBinomial
from scvi.module import Classifier
from scvi.module.base import BaseModuleClass, auto_move_data
from scvi.nn import Encoder, DecoderSCVI
from torch.distributions import Normal
from torch.distributions.kl import kl_divergence as kl
from torchmetrics.functional import accuracy, pearson_corrcoef, r2_score

from ._metrics import knn_purity
from ._utils import PerturbationNetwork, VanillaEncoder, CPA_REGISTRY_KEYS


class CPAModule(BaseModuleClass):
    """
    CPA module using Gaussian/NegativeBinomial Likelihood

    Parameters
    ----------
        n_genes: int
            Number of input genes
        n_treatments: int
            Number of total different treatments (single/combinatorial)
        covars_encoder: dict
            Dictionary of covariates with keys as each covariate name and values as
                number of unique values of the corresponding covariate
        n_latent: int
            dimensionality of the latent space
        recon_loss: str
            Autoencoder loss (either "gauss", "nb" or "zinb")
        doser_type: str
            Type of dosage network (either "logsigm", "sigm", or "linear")
        n_hidden_encoder: int

        n_layers_encoder: int

        use_batch_norm_encoder: bool

        use_layer_norm_encoder: bool

        variational: bool
    """

    def __init__(self,
                 n_genes: int,
                 n_perts: int,
                 n_adv_perts: int,
                 covars_encoder: dict,
                 n_latent: int = 128,
                 recon_loss: str = "gauss",
                 doser_type: str = "logsigm",
                 n_hidden_encoder: int = 256,
                 n_layers_encoder: int = 3,
                 n_hidden_decoder: int = 256,
                 n_layers_decoder: int = 3,
                 n_hidden_adv: int = 64,
                 n_layers_adv: int = 2,
                 n_hidden_doser: int = 128,
                 n_layers_doser: int = 2,
                 use_batch_norm_encoder: bool = True,
                 use_layer_norm_encoder: bool = False,
                 use_batch_norm_decoder: bool = True,
                 use_layer_norm_decoder: bool = False,
                 use_batch_norm_adv: bool = True,
                 use_layer_norm_adv: bool = False,
                 dropout_rate_encoder: float = 0.0,
                 dropout_rate_decoder: float = 0.0,
                 dropout_rate_adv: float = 0.0,
                 variational: bool = False,
                 seed: int = 0,
                 ):
        super().__init__()

        recon_loss = recon_loss.lower()
        assert recon_loss in ['gauss', 'zinb', 'nb']

        torch.manual_seed(seed)
        np.random.seed(seed)
        settings.seed = seed

        self.n_genes = n_genes
        self.n_perts = n_perts
        self.n_adv_perts = n_adv_perts
        self.n_latent = n_latent
        self.recon_loss = recon_loss
        self.doser_type = doser_type
        self.variational = variational

        self.covars_encoder = covars_encoder

        if variational:
            self.encoder = Encoder(
                n_genes,
                n_latent,
                var_activation=nn.Softplus(),
                n_hidden=n_hidden_encoder,
                n_layers=n_layers_encoder,
                use_batch_norm=use_batch_norm_encoder,
                use_layer_norm=use_layer_norm_encoder,
                dropout_rate=dropout_rate_encoder,
                activation_fn=nn.ReLU,
            )
        else:
            self.encoder = VanillaEncoder(
                n_input=n_genes,
                n_output=n_latent,
                n_cat_list=[],
                n_hidden=n_hidden_encoder,
                n_layers=n_layers_encoder,
                use_batch_norm=use_batch_norm_encoder,
                use_layer_norm=use_layer_norm_encoder,
                dropout_rate=dropout_rate_encoder,
                activation_fn=nn.ReLU,
                output_activation='linear',
            )

        # Decoder components
        if self.recon_loss in ['zinb', 'nb']:
            print(self.recon_loss)
            # setup the parameters of your generative model, as well as your inference model
            self.px_r = torch.nn.Parameter(torch.randn(self.n_genes))

            # l encoder goes from n_input-dimensional data to 1-d library size
            self.library_encoder = Encoder(
                self.n_genes,
                1,
                n_layers=1,
                n_hidden=128,
                dropout_rate=dropout_rate_decoder,
            )

            # decoder goes from n_latent-dimensional space to n_input-d data
            self.decoder = DecoderSCVI(
                n_input=n_latent,
                n_output=n_genes,
                n_layers=n_layers_decoder,
                n_hidden=n_hidden_decoder,
                use_batch_norm=use_batch_norm_decoder,
                use_layer_norm=use_layer_norm_decoder,
            )

        elif recon_loss == "gauss":
            self.decoder = Encoder(n_input=n_latent,
                                   n_output=n_genes,
                                   n_layers=n_layers_decoder,
                                   n_hidden=n_hidden_decoder,
                                   dropout_rate=dropout_rate_decoder,
                                   use_batch_norm=use_batch_norm_decoder,
                                   use_layer_norm=use_layer_norm_decoder,
                                   var_activation=None,
                                   )

        else:
            raise Exception('Invalid Loss function for Autoencoder')

        # Embeddings
        # 1. Drug Network
        self.pert_network = PerturbationNetwork(n_perts=n_perts,
                                                n_latent=n_latent,
                                                doser_type=doser_type,
                                                n_hidden=n_hidden_doser,
                                                n_layers=n_layers_doser,
                                                )

        self.perturbation_classifier = Classifier(
            n_input=n_latent,
            n_labels=n_adv_perts,
            n_hidden=n_hidden_adv,
            n_layers=n_layers_adv,
            use_batch_norm=use_batch_norm_adv,
            use_layer_norm=use_layer_norm_adv,
            dropout_rate=dropout_rate_adv,
            activation_fn=nn.ReLU,
            logits=True,
        )

        # 2. Covariates Embedding
        self.covars_embeddings = nn.ModuleDict(
            {
                key: torch.nn.Embedding(len(unique_covars), n_latent)
                for key, unique_covars in self.covars_encoder.items()
            }
        )

        self.covars_classifiers = nn.ModuleDict(
            {
                key: Classifier(n_input=n_latent,
                                n_labels=len(unique_covars),
                                n_hidden=self.n_hidden_adv,
                                n_layers=self.n_layers_adv,
                                use_batch_norm=use_batch_norm_encoder,
                                use_layer_norm=use_layer_norm_encoder,
                                dropout_rate=dropout_rate_encoder,
                                logits=True)
                if len(unique_covars) > 1 else None

                for key, unique_covars in self.covars_encoder.items()
            }
        )

        self.adv_loss_fn = nn.CrossEntropyLoss()

        self.metrics = {
            'pearson_r': pearson_corrcoef,
            'r2_score': r2_score
        }

    def _get_inference_input(self, tensors):
        x = tensors[CPA_REGISTRY_KEYS.X_KEY]  # batch_size, n_genes
        perts = tensors[CPA_REGISTRY_KEYS.PERTURBATIONS]
        perts_doses = tensors[CPA_REGISTRY_KEYS.PERTURBATIONS_DOSAGES]

        covars_dict = dict()
        for covar, unique_covars in self.covars_encoder.items():
            encoded_covars = tensors[covar].view(-1, )  # (batch_size,)
            covars_dict[covar] = encoded_covars

        return dict(
            x=x,
            perts=perts,
            perts_doses=perts_doses,
            covars_dict=covars_dict,
        )

    @auto_move_data
    def inference(
            self,
            x,
            perts,
            perts_doses,
            covars_dict,
            mixup_lambda: float = 1.0,
    ):
        batch_size = x.shape[0]

        if self.recon_loss in ['nb', 'zinb']:
            # log the input to the variational distribution for numerical stability
            x_ = torch.log(1 + x)
            ql_m, ql_v, library = self.library_encoder(x_)
        else:
            x_ = x
            ql_m, ql_v, library = None, None, None

        if self.variational:
            qz_m, qz_v, z_basal = self.encoder(x_)
        else:
            qz_m, qz_v, z_basal = None, None, self.encoder(x_)

        z_pert = self.pert_network(perts, perts_doses)  # (batch_size, n_latent)

        z_covs = torch.zeros_like(z_pert)
        for covar, encoder in self.covars_encoder.items():
            z_cov = self.covars_embedding[covar](covars_dict[covar].long())
            if len(encoder) > 1:
                z_cov_mixup = self.covars_embedding[covar](covars_dict[covar + '_mixup'].long())
                z_cov = mixup_lambda * z_cov + (1. - mixup_lambda) * z_cov_mixup
            z_cov = z_cov.view(batch_size, self.n_latent)  # batch_size, n_latent
            z_covs += z_cov

        z = z_basal + z_pert + z_covs

        return dict(
            z=z,
            z_basal=z_basal,
            z_covs=z_covs,
            z_pert=z_pert,
            library=library,
            qz_m=qz_m,
            qz_v=qz_v,
            ql_m=ql_m,
            ql_v=ql_v
        )

    def _get_generative_input(self, tensors, inference_outputs, **kwargs):
        z = inference_outputs["z"]
        library = inference_outputs['library']

        return dict(
            z=z,
            library=library,
        )

    @auto_move_data
    def generative(
            self,
            z,
            library=None,
    ):
        if self.recon_loss == 'nb':
            px_scale, _, px_rate, px_dropout = self.decoder("gene", z, library)
            px_r = torch.exp(self.px_r)

            dist_px = NegativeBinomial(mu=px_rate, theta=px_r)

        elif self.recon_loss == 'zinb':
            px_scale, _, px_rate, px_dropout = self.decoder("gene", z, library)
            px_r = torch.exp(self.px_r)

            dist_px = ZeroInflatedNegativeBinomial(mu=px_rate, theta=px_r, zi_logits=px_dropout)

        else:
            px_mean, px_var, x_pred = self.decoder(z)

            dist_px = Normal(loc=px_mean, scale=px_var.sqrt())

        return dict(dist_px=dist_px)

    def loss(self, tensors, inference_outputs, generative_outputs):
        """Computes the reconstruction loss (AE) or the ELBO (VAE)"""
        x = tensors[CPA_REGISTRY_KEYS.X_KEY]

        dist_px = generative_outputs['dist_px']
        recon_loss = -dist_px.log_prob(x).mean(dim=-1).mean()

        if self.variational:
            qz_m = inference_outputs["qz_m"]
            qz_v = inference_outputs["qz_v"]

            mean = torch.zeros_like(qz_m)
            scale = torch.ones_like(qz_v)

            kl_divergence_z = kl(Normal(qz_m, torch.sqrt(qz_v)), Normal(mean, scale)).sum(dim=1)
            kl_loss = kl_divergence_z.mean()
        else:
            kl_loss = torch.zeros_like(recon_loss)

        return recon_loss, kl_loss

    def adversarial_loss(self, tensors, z_basal, mixup_lambda: float = 1.0):
        """Computes adversarial classification losses and regularizations"""
        batch_size = tensors[CPA_REGISTRY_KEYS.X_KEY].shape[0]

        covars_dict = dict()
        for covar, unique_covars in self.covars_encoder.items():
            encoded_covars = tensors[covar].view(-1, )  # (batch_size,)
            covars_dict[covar] = encoded_covars

        covars_pred = {}
        for covar in self.covars_encoder.keys():
            if self.covars_classifiers[covar] is not None:
                covar_pred = self.covars_classifiers[covar](z_basal)
                covars_pred[covar] = covar_pred
            else:
                covars_pred[covar] = None

        adv_results = {}

        # Classification losses for different covariates
        for covar, covars in self.covars_encoder.items():
            adv_results[f'adv_{covar}'] = mixup_lambda * self.adv_loss_fn(
                covars_pred[covar],
                covars_dict[covar].long(),
            ) if covars_pred[covar] is not None else torch.as_tensor(0.0).to(self.device) + (
                    1. - mixup_lambda) * self.adv_loss_covariates(
                covars_pred[covar],
                covars_dict[covar + '_mixup'].long(),
            ) if covars_pred[covar] is not None else torch.as_tensor(0.0).to(self.device)
            adv_results[f'acc_{covar}'] = accuracy(
                covars_pred[covar].argmax(1), covars_dict[covar].long(), task='multiclass',
                num_classes=len(covars)) \
                if covars_pred[covar] is not None else torch.as_tensor(0.0).to(self.device)

        adv_results['adv_loss'] = sum([adv_results[f'adv_{key}'] for key in self.covars_encoder.keys()])

        perturbations = tensors[CPA_REGISTRY_KEYS.PERTURBATION_KEY].view(-1, )
        perturbations_mixup = tensors[CPA_REGISTRY_KEYS.PERTURBATION_KEY + '_mixup'].view(-1, )

        perturbations_pred = self.perturbation_classifier(z_basal)

        adv_results['adv_perts'] = mixup_lambda * self.adv_loss_fn(perturbations_pred,
                                                                   perturbations.long()) + (
                                           1. - mixup_lambda) * self.adv_loss_fn(perturbations_pred,
                                                                                 perturbations_mixup.long())

        adv_results['acc_perts'] = mixup_lambda * accuracy(
            perturbations_pred.argmax(1), perturbations.long().view(-1, ), average='macro',
            num_classes=self.n_adv_perts, task='multiclass',
        ) + (1. - mixup_lambda) * accuracy(
            perturbations_pred.argmax(1), perturbations_mixup.long().view(-1, ), average='macro',
            num_classes=self.n_adv_perts, task='multiclass',
        )

        adv_results['adv_loss'] += adv_results['adv_perts']

        # Penalty losses
        for covar in self.covars_encoder.keys():
            adv_results[f'penalty_{covar}'] = (
                torch.autograd.grad(
                    covars_pred[covar].sum(),
                    z_basal,
                    create_graph=True
                )[0].pow(2).mean()
            ) if covars_pred[covar] is not None else torch.as_tensor(0.0).to(self.device)

        adv_results['penalty_adv'] = sum([adv_results[f'penalty_{covar}'] for covar in self.covars_encoder.keys()])

        adv_results['penalty_perts'] = (
            torch.autograd.grad(
                perturbations_pred.sum(),
                z_basal,
                create_graph=True,
            )[0].pow(2).mean()
        )

        adv_results['penalty_adv'] += adv_results['penalty_perts']

        return adv_results

    def r2_metric(self, tensors, inference_outputs, generative_outputs, mode: str = 'lfc'):
        mode = mode.lower()
        assert mode.lower() in ['direct']

        x = tensors[CPA_REGISTRY_KEYS.X_KEY]  # batch_size, n_genes

        batch_size = x.shape[0]

        indices = tensors[CPA_REGISTRY_KEYS.PERTURBATION_KEY].view(-1, )  # (batch_size,)

        r2_mean = torch.tensor(0.0, device=indices.device)
        r2_var = torch.tensor(0.0, device=indices.device)

        x_pred = generative_outputs['dist_px'].sample()
        x_pred = torch.nan_to_num(x_pred, nan=0, posinf=1e3, neginf=-1e3)

        if self.recon_loss in ['nb', 'zinb']:
            x = torch.log(1 + x)
            x_pred = torch.log(1 + x_pred)

        if mode == 'lfc':
            x_ctrl = tensors[CPA_REGISTRY_KEYS.X_CTRL_KEY]  # batch_size, n_genes

            x_true = torch.abs(x - x_ctrl)
            x_pred = torch.abs(x_pred - x_ctrl)

            if 'deg_mask_r2' in tensors.keys():
                deg_mask = tensors['deg_mask_r2']

                x_true *= deg_mask
                x_pred *= deg_mask

        else:
            x_true = x

            if f'{CPA_REGISTRY_KEYS.DEG_MASK}_r2' in tensors.keys():
                deg_mask = tensors[f'{CPA_REGISTRY_KEYS.DEG_MASK}_r2']

                x_true *= deg_mask
                x_pred *= deg_mask

        unique_indices = indices.unique()
        n_unique_indices = len(unique_indices)

        for index in unique_indices:
            index_mask = (indices == index)

            x_true_index = x_true[index_mask]
            x_pred_index = x_pred[index_mask]

            x_true_index_mean = x_true_index.mean(0)
            x_true_index_var = x_true_index.var(0)

            x_pred_index_mean = x_pred_index.mean(0)
            x_pred_index_var = x_pred_index.var(0)

            if mode == 'lfc':
                r2_mean += torch.nan_to_num(self.metrics['pearson_r'](x_pred_index_mean, x_true_index_mean),
                                            nan=0.0).item() / n_unique_indices
                r2_var += torch.nan_to_num(self.metrics['pearson_r'](x_pred_index_var, x_true_index_var),
                                           nan=0.0).item() / n_unique_indices
            else:
                # print(x_pred_index_mean.device, x_true_index_mean.device)
                r2_mean += torch.nan_to_num(self.metrics['r2_score'](x_pred_index_mean, x_true_index_mean),
                                            nan=0.0).item() / n_unique_indices
                r2_var += torch.nan_to_num(self.metrics['r2_score'](x_pred_index_var.cpu(), x_true_index_var.cpu()),
                                           nan=0.0).item() / n_unique_indices

        return r2_mean.detach().cpu(), r2_var.detach().cpu()

    def mixup_data(self, tensors, alpha: float = 0.0):
        """
            Returns mixed inputs, pairs of targets, and lambda
        """
        alpha = max(0.0, alpha)

        if alpha == 0.0:
            mixup_lambda = 1.0
        else:
            mixup_lambda = np.random.beta(alpha, alpha)

        x = tensors[CPA_REGISTRY_KEYS.X_KEY]
        y_perturbations = tensors[CPA_REGISTRY_KEYS.PERTURBATION_KEY]
        perturbations = tensors[CPA_REGISTRY_KEYS.PERTURBATIONS]
        perturbations_dosages = tensors[CPA_REGISTRY_KEYS.PERTURBATIONS_DOSAGES]

        batch_size = x.size()[0]
        index = torch.randperm(batch_size).to(x.device)

        mixed_x = mixup_lambda * x + (1. - mixup_lambda) * x[index, :]

        tensors[CPA_REGISTRY_KEYS.X_KEY] = mixed_x
        tensors[CPA_REGISTRY_KEYS.X_KEY + '_true'] = x
        tensors[CPA_REGISTRY_KEYS.X_KEY + '_mixup'] = x[index]
        tensors[CPA_REGISTRY_KEYS.PERTURBATION_KEY + '_mixup'] = y_perturbations[index]
        tensors[CPA_REGISTRY_KEYS.PERTURBATIONS] = perturbations
        tensors[CPA_REGISTRY_KEYS.PERTURBATIONS + '_mixup'] = perturbations[index]
        tensors[CPA_REGISTRY_KEYS.PERTURBATIONS_DOSAGES] = perturbations_dosages
        tensors[CPA_REGISTRY_KEYS.PERTURBATIONS_DOSAGES + '_mixup'] = perturbations_dosages[index]

        for covar, encoder in self.covars_encoder.items():
            tensors[covar + '_mixup'] = tensors[covar][index]

        return tensors, mixup_lambda

    def disentanglement(self, tensors, inference_outputs, generative_outputs, linear=True):
        z_basal = inference_outputs['z_basal'].detach().cpu().numpy()
        z = inference_outputs['z'].detach().cpu().numpy()

        perturbations = tensors[CPA_REGISTRY_KEYS.PERTURBATION_KEY].view(-1, )
        perturbations_names = perturbations.detach().cpu().numpy()

        knn_basal = knn_purity(z_basal, perturbations_names.ravel(),
                               n_neighbors=min(perturbations_names.shape[0] - 1, 30))
        knn_after = knn_purity(z, perturbations_names.ravel(),
                               n_neighbors=min(perturbations_names.shape[0] - 1, 30))

        for covar, unique_covars in self.covars_encoder.items():
            if len(unique_covars) > 1:
                target_covars = tensors[f'{covar}'].detach().cpu().numpy()

                knn_basal += knn_purity(z_basal, target_covars.ravel(),
                                        n_neighbors=min(target_covars.shape[0] - 1, 30))

                knn_after += knn_purity(z, target_covars.ravel(),
                                        n_neighbors=min(target_covars.shape[0] - 1, 30))

        return knn_basal, knn_after

    def get_expression(self, tensors, **inference_kwargs):
        """Computes gene expression means and std.

        Only implemented for the gaussian likelihood.

        Parameters
        ----------
        tensors : dict
            Considered inputs

        """
        tensors, _ = self.mixup_data(tensors, alpha=0.0)
        _, generative_outputs = self.forward(
            tensors,
            compute_loss=False,
        )

        dist_px = generative_outputs['dist_px']

        return dist_px.sample().detach().cpu().numpy()

    def get_pert_embeddings(self, tensors, **inference_kwargs):
        inputs = self._get_inference_input(tensors)
        drugs = inputs['perts']
        doses = inputs['perts_doses']

        return self.pert_network(drugs, doses)
