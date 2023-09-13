from typing import List, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F
from scvi.distributions import NegativeBinomial

from scvi.nn import FCLayers
from torch.distributions import Normal


class _REGISTRY_KEYS:
    X_KEY: str = "X"
    X_CTRL_KEY: str = None
    PERTURBATION_KEY: str = None
    PERTURBATIONS: str = "perts"
    PERTURBATIONS_DOSAGES: str = "perts_doses"
    SIZE_FACTOR_KEY: str = "size_factor"
    CAT_COV_KEYS: List[str] = []
    MAX_COMB_LENGTH: int = 2
    CONTROL_KEY: str = None
    DEG_MASK: str = None
    DEG_MASK_R2: str = None
    PADDING_IDX: int = 0


CPA_REGISTRY_KEYS = _REGISTRY_KEYS()


class VanillaEncoder(nn.Module):
    def __init__(
            self,
            n_input,
            n_output,
            n_hidden,
            n_layers,
            n_cat_list,
            use_layer_norm=True,
            use_batch_norm=False,
            output_activation: str = 'linear',
            dropout_rate: float = 0.1,
            activation_fn=nn.ReLU,
    ):
        super().__init__()
        self.n_output = n_output
        self.output_activation = output_activation

        self.network = FCLayers(
            n_in=n_input,
            n_out=n_hidden,
            n_cat_list=n_cat_list,
            n_layers=n_layers,
            n_hidden=n_hidden,
            use_layer_norm=use_layer_norm,
            use_batch_norm=use_batch_norm,
            dropout_rate=dropout_rate,
            activation_fn=activation_fn,
        )
        self.z = nn.Linear(n_hidden, n_output)

    def forward(self, inputs, *cat_list):
        z = self.z(self.network(inputs, *cat_list))
        return z


class GeneralizedSigmoid(nn.Module):
    """
    Sigmoid, log-sigmoid or linear functions for encoding dose-response for
    drug perurbations.
    """

    def __init__(self, n_drugs, non_linearity='sigmoid'):
        """Sigmoid modeling of continuous variable.
        Params
        ------
        nonlin : str (default: logsigm)
            One of logsigm, sigm.
        """
        super(GeneralizedSigmoid, self).__init__()
        self.non_linearity = non_linearity
        self.n_drugs = n_drugs
        self.beta = torch.nn.Parameter(
            torch.ones(1, n_drugs),
            requires_grad=True
        )
        self.bias = torch.nn.Parameter(
            torch.zeros(1, n_drugs),
            requires_grad=True
        )

        self.vmap = None

    def forward(self, x, y):
        """
            Parameters
            ----------
            x: (batch_size, max_comb_len)
            y: (batch_size, max_comb_len)
        """
        y = y.long()
        if self.non_linearity == 'logsigm':
            bias = self.bias[0][y]
            beta = self.beta[0][y]
            c0 = bias.sigmoid()
            return (torch.log1p(x) * beta + bias).sigmoid() - c0
        elif self.non_linearity == 'sigm':
            bias = self.bias[0][y]
            beta = self.beta[0][y]
            c0 = bias.sigmoid()
            return (x * beta + bias).sigmoid() - c0
        else:
            return x

    def one_drug(self, x, i):
        if self.non_linearity == 'logsigm':
            c0 = self.bias[0][i].sigmoid()
            return (torch.log1p(x) * self.beta[0][i] + self.bias[0][i]).sigmoid() - c0
        elif self.non_linearity == 'sigm':
            c0 = self.bias[0][i].sigmoid()
            return (x * self.beta[0][i] + self.bias[0][i]).sigmoid() - c0
        else:
            return x


class PerturbationNetwork(nn.Module):
    def __init__(self,
                 n_perts,
                 n_latent,
                 doser_type='logsigm',
                 n_hidden=None,
                 n_layers=None,
                 dropout_rate: float = 0.0):
        super().__init__()
        self.n_latent = n_latent
        self.pert_embedding = nn.Embedding(n_perts + 1, n_latent, padding_idx=CPA_REGISTRY_KEYS.PADDING_IDX)
        self.doser_type = doser_type
        if self.doser_type == 'mlp':
            self.dosers = nn.ModuleList()
            for _ in range(n_perts):
                self.dosers.append(
                    FCLayers(
                        n_in=1,
                        n_out=1,
                        n_hidden=n_hidden,
                        n_layers=n_layers,
                        use_batch_norm=False,
                        use_layer_norm=True,
                        dropout_rate=dropout_rate
                    )
                )
        else:
            self.dosers = GeneralizedSigmoid(n_perts, non_linearity=self.doser_type)

    def forward(self, perts, dosages):
        """
            perts: (batch_size, max_comb_len)
            dosages: (batch_size, max_comb_len)
        """
        perts = perts.long()
        scaled_dosages = self.dosers(dosages, perts)  # (batch_size, max_comb_len)
        drug_embeddings = self.pert_embedding(perts)  # (batch_size, max_comb_len, n_latent)
        return torch.einsum('bm,bme->bme', [scaled_dosages, drug_embeddings]).sum(
            dim=1)  # (batch_size, n_latent)
