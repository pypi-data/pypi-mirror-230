# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Callable, Optional

from overrides import overrides
from torch.utils.data import Dataset
from torchvision.datasets import Flowers102
from torchvision.transforms import ToTensor

from archai.api.dataset_provider import DatasetProvider


class Flowers102DatasetProvider(DatasetProvider):
    """Oxford 102 Flower dataset provider."""

    def __init__(
        self,
        root: Optional[str] = "dataroot",
    ) -> None:
        """Initialize Oxford 102 Flower dataset provider.

        Args:
            root: Root directory of dataset where is saved.

        """

        super().__init__()

        self.root = root

    @overrides
    def get_train_dataset(
        self,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
    ) -> Dataset:
        return Flowers102(
            self.root,
            split="train",
            transform=transform or ToTensor(),
            target_transform=target_transform,
            download=True,
        )

    @overrides
    def get_val_dataset(
        self,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
    ) -> Dataset:
        return Flowers102(
            self.root,
            split="val",
            transform=transform or ToTensor(),
            target_transform=target_transform,
            download=True,
        )

    @overrides
    def get_test_dataset(
        self,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
    ) -> Dataset:
        return Flowers102(
            self.root,
            split="test",
            transform=transform or ToTensor(),
            target_transform=target_transform,
            download=True,
        )
