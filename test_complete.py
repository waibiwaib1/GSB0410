import numpy as np
import matplotlib.pyplot as plt

print("=== 完整测试 ===")

# 测试1：先设置反转的 ylim，再设置 log 缩放
print("\n测试1：先设置反转的 ylim，再设置 log 缩放")
fig, ax = plt.subplots()
y = np.linspace(1, 100000, 100)
x = np.linspace(0, 1, 100)
ax.plot(x, y)
print(f"  初始 ylim: {ax.get_ylim()}")
ax.set_ylim(y.max(), y.min())
print(f"  设置反转 ylim 后: {ax.get_ylim()}")
print(f"  y-axis inverted: {ax.yaxis_inverted()}")
ax.set_yscale('log')
print(f"  设置 log 缩放后: {ax.get_ylim()}")
print(f"  y-axis inverted: {ax.yaxis_inverted()}")
plt.close(fig)

# 测试2：先设置 log 缩放，再设置反转的 ylim
print("\n测试2：先设置 log 缩放，再设置反转的 ylim")
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_yscale('log')
print(f"  设置 log 缩放后初始 ylim: {ax.get_ylim()}")
ax.set_ylim(y.max(), y.min())
print(f"  设置反转 ylim 后: {ax.get_ylim()}")
print(f"  y-axis inverted: {ax.yaxis_inverted()}")
plt.close(fig)

# 测试3：测试 x 轴
print("\n测试3：测试 x 轴")
fig, ax = plt.subplots()
ax.plot(y, x)
ax.set_xscale('log')
print(f"  设置 log 缩放后初始 xlim: {ax.get_xlim()}")
ax.set_xlim(y.max(), y.min())
print(f"  设置反转 xlim 后: {ax.get_xlim()}")
print(f"  x-axis inverted: {ax.xaxis_inverted()}")
plt.close(fig)

print("\n=== 所有测试完成！ ===")
