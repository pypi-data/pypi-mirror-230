import numpy as np
import torch
from torch.optim.lr_scheduler import _LRScheduler


class CosineWithRestarts(_LRScheduler):
    """
    Cosine annealing with restarts.
    Copy From https://github.com/allenai/allennlp/issues/1642

    Parameters
    ----------
    optimizer : torch.optim.Optimizer

    T_max : int
        The maximum number of iterations within the first cycle.

    eta_min : float, optional (default: 0)
        The minimum learning rate.

    last_epoch : int, optional (default: -1)
        The index of the last epoch.

    """

    def __init__(self, optimizer: torch.optim.Optimizer, T_max: int, eta_min: float = 0., last_epoch: int = -1, factor: float = 1.) -> None:
        # pylint: disable=invalid-name
        self.T_max = T_max
        self.eta_min = eta_min
        self.factor = factor
        self._last_restart = 0
        self._cycle_counter = 0
        self._cycle_factor = 1.
        self._updated_cycle_len = T_max
        self._initialized = False
        super(CosineWithRestarts, self).__init__(optimizer, last_epoch)

    def get_lr(self):
        """Get updated learning rate."""
        # HACK: We need to check if this is the first time get_lr() was called, since
        # we want to start with step = 0, but _LRScheduler calls get_lr with
        # last_epoch + 1 when initialized.
        if not self._initialized:
            self._initialized = True
            return self.base_lrs
        step = self.last_epoch + 1
        self._cycle_counter = step - self._last_restart
        lrs = [(self.eta_min + ((lr - self.eta_min) / 2) * (np.cos(np.pi * ((self._cycle_counter) % self._updated_cycle_len) / self._updated_cycle_len) + 1))
               for lr in self.base_lrs]
        if self._cycle_counter % self._updated_cycle_len == 0:
            # Adjust the cycle length.
            self._cycle_factor *= self.factor
            self._cycle_counter = 0
            self._updated_cycle_len = int(self._cycle_factor * self.T_max)
            self._last_restart = step
        return lrs


if __name__ == '__main__':
    test_last_epoch = -1
    test_optimizer = torch.optim.SGD([torch.zeros(8)], lr=0.02)
    for group in test_optimizer.param_groups:
        group.setdefault('initial_lr', group['lr'])
    test_scheduler = torch.optim.lr_scheduler.MultiStepLR(test_optimizer, [3, 6], 0.1, last_epoch=test_last_epoch)
    global_step = 0
    for epoch in range(2, 10):
        for step in range(20):
            test_optimizer.step()
            # use warm-up iteration lr
            if global_step < 15:
                lr_scale = min(1., float(global_step + 1) / 15.)
                for pg in test_optimizer.param_groups:
                    pg['lr'] = lr_scale * 0.02  # get_last_lr is from pg['lr']
            global_step += 1
            print(epoch, global_step, test_scheduler.get_last_lr(), test_optimizer.param_groups[0]['lr'])
        test_scheduler.step()  # epoch lr_scheduler
