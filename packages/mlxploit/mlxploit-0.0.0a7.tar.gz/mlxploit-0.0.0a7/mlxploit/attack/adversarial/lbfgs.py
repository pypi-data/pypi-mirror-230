import numpy as np
from rich.console import Console
import scipy.optimize as so
import torch
import torch.nn.functional as F
from typing import Any, Dict


class AdversarialLBFGS:
    """
    Adversarial attack with L-BFGS (Limited-memory BFGS method)
    Reference: https://arxiv.org/pdf/1712.07107.pdf#subsection.4.1
    """

    @staticmethod
    def params() -> Dict:
        return {
            'epsilon': 1e-4,
            'maxiter': 20,
            'clip_max': 1,
            'clip_min': 0,
            'class_num': 10
        }

    
    @staticmethod
    def calc_distance(x,y):
        x = torch.from_numpy(x).double()
        y = torch.from_numpy(y).double()

        dist_squ = torch.norm(x - y)
        return dist_squ **2

    
    @staticmethod
    def loss(model, x0, x, c, dtype, shape, target_dist):
        #calculate the target function 
        v1 = AdversarialLBFGS.calc_distance(x0,x)
            
        x = torch.tensor(x.astype(dtype).reshape(shape))
        x = x.unsqueeze_(0).float()

        predict = model(x)
        v2 = F.nll_loss(predict, target_dist)
            
        v = c * v1 + v2
        #print(v)
        return np.float64(v)


    @staticmethod
    def generate(
        console: Console,
        model: Any,
        original_image_batch: Any,
        target_idx: int,
    ) -> None:
        """
        A main function to generate adversarial examples with L-BFGS.
        """
        console.print(":brain: Start generating adversarial examples with L-BFGS...")
        # Generate adversarial examples
        target_dist = torch.tensor(target_idx)
        target_dist = target_dist.unsqueeze_(0).long()
        params = AdversarialLBFGS.params()
        epsilon = params['epsilon']
        max_ = params['clip_max']
        min_ = params['clip_min']
        maxiter = params['maxiter']

        # Set values for LBFGS
        x0 = original_image_batch[0].numpy()
        shape = x0.shape
        dtype = x0.dtype
        x0 = x0.flatten().astype(np.float64)
        n = len(x0)
        bounds = [(min_, max_)] * n
        
        # Find initial c
        c = epsilon
        console.print(f":eyes: Finding initial c...")
        for i in range(30):
            c = 2 * c
            x_new, is_adversarial = AdversarialLBFGS.lbfgs_b(
                console=console, model=model, x0=x0, dtype=dtype, shape=shape, target_dist=target_dist,
                max_=max_, min_=min_, c=c, bounds=bounds, maxiter=maxiter, target_idx=target_idx)
            if is_adversarial is False:
                break

        console.print(":eyes: Start binary search:")
        if is_adversarial is True:
            console.print(":exclamation: Could not find an adversarial; maybe the model returns wrong gradients")
            return
        
        console.print(f"c_high: {c}")

        # Binary search
        c_low = 0
        c_high = c
        while c_high - c_low >= epsilon:
            console.print(f"{c_high} {c_low}")
            c_half = (c_low + c_high) / 2
            x_new, is_adversarial = AdversarialLBFGS.lbfgs_b(
                console=console, model=model, x0=x0, dtype=dtype, shape=shape, target_dist=target_dist,
                max_=max_, min_=min_, c=c_half, bounds=bounds, maxiter=maxiter, target_idx=target_idx)

            if is_adversarial:
                c_low = c_half
            else:
                c_high = c_low

        x_new, is_adversarial = AdversarialLBFGS.lbfgs_b(
            console=console, model=model, x0=x0, dtype=dtype, shape=shape, target_dist=target_dist,
            max_=max_, min_=min_, c=c_low, bounds=bounds, maxiter=maxiter, target_idx=target_idx)
        dis = AdversarialLBFGS.calc_distance(x_new, x0)
        mintargetfunc = AdversarialLBFGS.loss(model=model, x0=x0, x=x_new, c=c_low, dtype=dtype, shape=shape, target_dist=target_dist)

        x_new = x_new.astype(dtype)
        x_new = x_new.reshape(shape)
        x_new = torch.from_numpy(x_new)

        adv_tensor, dis, loss, value_of_c = x_new, dis, mintargetfunc, c_low
        adv_tensor = adv_tensor.unsqueeze_(0).float()

        # Test the adversarial example
        adv_pred = model(adv_tensor)
        adv_pred = adv_pred.argmax(dim=1, keepdim=True)

        if adv_pred == target_idx:
            console.print(":star_struck: Fooled the model successfully!")
        else:
            console.print(":diggy_face: Could not fool the model...")

        return None


    @staticmethod
    def lbfgs_b(console: Console, model: Any, x0, dtype, shape, target_dist, max_, min_, c, bounds, maxiter, target_idx):

        def _loss(x, c):
            #calculate the target function 
            v1 = AdversarialLBFGS.calc_distance(x0,x)
                
            x = torch.tensor(x.astype(dtype).reshape(shape))
            x = x.unsqueeze_(0).float()

            predict = model(x).logits
            v2 = F.nll_loss(predict, target_dist)
                
            v = c * v1 + v2
            #print(v)
            return np.float64(v)
        

        def pending_attack(model, adv_exp, target):
            adv_exp = adv_exp.reshape(shape).astype(dtype)
            adv_exp = torch.from_numpy(adv_exp)
            adv_exp = adv_exp.unsqueeze_(0).float()

            pred = model(adv_exp)
            label = pred.argmax(dim=1, keepdim=True)
            if label == target:
                return True
            else:
                return False
            

        # Initial variables
        approx_grad_eps = (max_ - min_) / 100
        console.print(f"LBFGS-B: c={c}")

        # Start optimization
        optimize_output, f, d = so.fmin_l_bfgs_b(
            _loss,
            x0,
            args=(c,),
            approx_grad=True,
            bounds=bounds,
            m=15,
            maxiter=maxiter,
            factr=1e10,
            maxls=5,
            epsilon=approx_grad_eps)
        console.print(":eyes: Finish optimization")

        # LBFGS-B does not always exactly respect the boundaries
        if np.amax(optimize_output) > max_ or np.amax(optimize_output) < min_:
            console.print(f"Input out of bounds (min, max = {np.min(optimize_output), np.amax(optimize_output)})")
            optimize_output = np.clip(optimize_output, min_, max_)

        is_adversarial = pending_attack(model=model, adv_exp=optimize_output, target=target_idx)
            
        return optimize_output, is_adversarial

