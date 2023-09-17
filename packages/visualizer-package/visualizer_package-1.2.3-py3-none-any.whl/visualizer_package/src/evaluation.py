import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from sklearn.cluster import DBSCAN

from utils import *

def filter_unuseful(points):
	xValid = np.all([clstCfg['ylim'][0] <= points[:, 0], points[:, 0] <= clstCfg['ylim'][1]], axis=0)
	yValid = np.all([clstCfg['xlim'][0] <= points[:, 1], points[:, 1] <= clstCfg['xlim'][1]], axis=0)
	zValid = np.all([clstCfg['zlim'][0] <= points[:, 2], points[:, 2] <= clstCfg['zlim'][1]], axis=0)
	return points[np.all([xValid, yValid, zValid], axis=0)]


def get_cluster(dbscan, points):
	clustering = dbscan.fit(points)
	category = dict()
	for label in np.unique(clustering.labels_):
		if label != -1:
			category[label] = points[clustering.labels_==label]
	return clustering.labels_, category


def plot_cluster_bounding(x, y, category, fig, ax, title):
	boxes = []
	margin = 1
	for label in category.keys():
		bottomLeft = np.min(category[label], axis=0)
		topRight = np.max(category[label], axis=0)
		boxes.append((bottomLeft, topRight))
	ax.scatter(x, y, s=1)
	for bottomLeft, topRight in boxes:
		xMin = bottomLeft[1]
		yMin = bottomLeft[0]
		width = topRight[1] - xMin + 2 * margin
		height = topRight[0] - yMin + 2 * margin
		rect = Rectangle((xMin - margin, yMin - margin), width, height, fill=False, color='red', linewidth=1)
		ax.add_patch(rect)
	ax.set_xlim(clstCfg['xlim'][0], clstCfg['xlim'][1])
	ax.set_ylim(clstCfg['ylim'][0], clstCfg['ylim'][1])
	ax.set_xlabel('Azimuth Position')
	ax.set_ylabel('Depth Position')
	ax.set_title(title)
