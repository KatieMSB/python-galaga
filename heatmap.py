import matplotlib.pyplot as plt
from collections import Counter

def load_x_positions(filename):
    x_positions = []
    with open(filename, "r") as file:
        for line in file:
            try:
                x, _ = map(int, line.strip().split(","))
                x_positions.append(x)
            except ValueError:
                continue
    return x_positions

x_positions1 = load_x_positions("player_positions_sra.txt")
x_positions2 = load_x_positions("player_positions_rla.txt")

x_counts1 = Counter(x_positions1)
x_counts2 = Counter(x_positions2)

all_x = sorted(set(x_counts1.keys()) | set(x_counts2.keys()))

counts1 = [x_counts1.get(x, 0) for x in all_x]
counts2 = [x_counts2.get(x, 0) for x in all_x]

plt.figure(figsize=(12, 5))
plt.bar(all_x, counts1, width=10.0, alpha=0.6, label="SRA", color='dodgerblue')
plt.bar(all_x, counts2, width=10.0, alpha=0.6, label="RLA", color='red')

plt.title("Player X Positions")
plt.xlabel("X Coordinate")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.show()
