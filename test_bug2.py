import numpy as np
import matplotlib.pyplot as plt

y = np.linspace(1000e2, 1, 100)
x = np.exp(-np.linspace(0, 1, y.size))

print("=== 测试1: 先设置缩放，再设置反转的 ylim ===")
for yscale in ('linear', 'log'):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_yscale(yscale)
    print(f"\nyscale: {yscale}")
    print(f"  调用 set_ylim({y.max()}, {y.min()})")
    result = ax.set_ylim(y.max(), y.min())
    print(f"  返回值: {result}")
    print(f"  get_ylim: {ax.get_ylim()}")
    print(f"  y-axis inverted: {ax.yaxis_inverted()}")
    plt.close(fig)

print("\n=== 测试2: 先设置 ylim，再设置缩放 ===")
for yscale in ('linear', 'log'):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    print(f"\nyscale: {yscale}")
    print(f"  调用 set_ylim({y.max()}, {y.min()})")
    ax.set_ylim(y.max(), y.min())
    ax.set_yscale(yscale)
    print(f"  get_ylim: {ax.get_ylim()}")
    print(f"  y-axis inverted: {ax.yaxis_inverted()}")
    plt.close(fig)
