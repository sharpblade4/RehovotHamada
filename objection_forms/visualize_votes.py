import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from collections import defaultdict
from typing import Dict, Tuple

g_coords = {}


def process_votes(df: pd.DataFrame, img: np.ndarray) -> Dict[str, int]:
    votes = defaultdict(int)
    for idx, row in df.iterrows():
        address = f"{row['street']}_{row['building']}"
        votes[address] += 1
        if address not in g_coords:
            print(f"{idx}/{len(df)} {address[::-1]}\t||\t{address} ?")
            res = _get_coords(img, address)
            with open('coordinates_incr', 'wb') as f:
                pickle.dump(g_coords, f)
    return votes


def visualize(votes: Dict[str, int], img: np.ndarray) -> None:
    radius_factor = 20
    plt.imshow(img)
    for address, vote_count in votes.items():
        plt.scatter(*g_coords[address], alpha=0.7, c='blue', s=radius_factor * vote_count)
    plt.show()


def _get_coords(image: np.adarray, address: str) -> Dict[str, Tuple[float, float]]:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(image)

    ix, iy = None, None

    def onclick(event):
        global ix, iy
        ix, iy = event.xdata, event.ydata
        print(ix, iy)
        fig.canvas.mpl_disconnect(cid)
        global g_coords
        g_coords[address] = (ix, iy)
        plt.close()
        return g_coords

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    global g_coords
    return g_coords


def main() -> None:
    df = pd.read_excel("street_normalzed.xlsx")
    df = df.sort_values(['street', 'building'])
    img = plt.imread('hamada_map.png')
    votes = process_votes(df, img)
    visualize(votes, img)


if __name__ == '__main__':
    # %history -f visualize_votes.py
    main()
