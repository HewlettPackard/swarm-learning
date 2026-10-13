## Results


### Node 0
| Experiment | Noise | Grad Thresh | Acc Thresh | ε | DP Drop Epoch | Training Time (s) | Final Test Acc | Final F1 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| exp_baseline_iid | 0.0 | — | — | — | — | 959.23 | 90.59% | 0.9057 |
| exp_full_dp_iid | 0.5 | — | — | 10.2567 | — | 2689.51 | 80.30% | 0.8027 |
| exp_cascaded_dp_noise0.5_iid | 0.5 | 0.15 | 0.0005 | 7.3731 | 8 | 1583.39 | 90.10% | 0.9009 |
| exp_full_dp_noise1.0_iid | 1.0 | — | — | 1.1915 | — | 2642.71 | 77.49% | 0.7602 |
| exp_cascaded_dp_noise1.0_iid | 1.0 | 0.4 | 0.0005 | 0.7859 | 16 | 1534.66 | 90.04% | 0.9005 |
| exp_full_dp_noise1.5_iid | 1.5 | — | — | 0.6301 | — | 2639.54 | 73.98% | 0.7247 |
| exp_cascaded_dp_noise1.5_iid | 1.5 | 0.4 | 0.0005 | 0.3072 | 11 | 1396.04 | 89.63% | 0.8963 |


### Node 1
| Experiment | Noise | Grad Thresh | Acc Thresh | ε | DP Drop Epoch | Training Time (s) | Final Test Acc | Final F1 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| exp_baseline_iid | 0.0 | — | — | — | — | 952.94 | 90.59% | 0.9057 |
| exp_full_dp_iid | 0.5 | — | — | 10.2567 | — | 2692.71 | 80.30% | 0.8027 |
| exp_cascaded_dp_noise0.5_iid | 0.5 | 0.15 | 0.0005 | 7.3731 | 8 | 1584.81 | 90.10% | 0.9009 |
| exp_full_dp_noise1.0_iid | 1.0 | — | — | 1.1915 | — | 2644.51 | 77.49% | 0.7602 |
| exp_cascaded_dp_noise1.0_iid | 1.0 | 0.4 | 0.0005 | 0.7859 | 16 | 1537.34 | 90.04% | 0.9005 |
| exp_full_dp_noise1.5_iid | 1.5 | — | — | 0.6301 | — | 2638.33 | 73.98% | 0.7247 |
| exp_cascaded_dp_noise1.5_iid | 1.5 | 0.4 | 0.0005 | 0.3072 | 11 | 1394.30 | 89.63% | 0.8963 |

> [!NOTE]
> For cascaded DP runs, the provided epsilon ($\varepsilon$) value only reflects the privacy budget consumed during the first stage before the DP cutoff. It does not serve as a metric for total privacy preservation.

## Results as Graphs
<img src="./Accuracy_Bar.png" width=50%>
<img src="./Runtime_Bar.png" width=50%>
