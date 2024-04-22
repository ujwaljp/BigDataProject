import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Example data (replace with your own)
categories = ['A', 'B', 'C', 'D', 'E']
data = np.random.randint(1, 100, size=(10, len(categories)))  # 10 frames, 5 categories

# Initialize plot
fig, ax = plt.subplots()

# Function to update pie chart with transition
def update(frame):
    ax.clear()
    # Interpolate data between two frames
    if frame < len(data) - 1:
        for i, category in enumerate(categories):
            interpolated_data = np.linspace(data[frame, i], data[frame + 1, i], num=10)
            ax.pie([interpolated_data[-1]], labels=[category], autopct='%1.1f%%')
    else:
        ax.pie(data[frame], labels=categories, autopct='%1.1f%%')
    ax.set_title(f'Frame {frame+1}')

# Animate pie chart
ani = animation.FuncAnimation(fig, update, frames=len(data), repeat=False)

plt.show()
