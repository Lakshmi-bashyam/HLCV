import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

import histogram_module
import dist_module

def rgb2gray(rgb):

    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray

#
# model_images - list of file names of model images
# query_images - list of file names of query images
#
# dist_type - string which specifies distance type:  'chi2', 'l2', 'intersect'
# hist_type - string which specifies histogram type:  'grayvalue', 'dxdy', 'rgb', 'rg'
#
# note: use functions 'get_dist_by_name', 'get_hist_by_name' and 'is_grayvalue_hist' to obtain 
#       handles to distance and histogram functions, and to find out whether histogram function 
#       expects grayvalue or color image
#

def find_best_match(model_images, query_images, dist_type, hist_type, num_bins):

  hist_isgray = histogram_module.is_grayvalue_hist(hist_type)

  model_hists = compute_histograms(model_images, hist_type, hist_isgray, num_bins)
  query_hists = compute_histograms(query_images, hist_type, hist_isgray, num_bins)

  D = np.zeros((len(model_images), len(query_images)))
  best_match = []
  # your code here
  for qid, query in enumerate(query_hists):
    for mid, model in enumerate(model_hists):
      D[mid, qid] = dist_module.get_dist_by_name(model, query, dist_type)
    best_match.append(np.argsort(D[:,qid])[0])

  return np.array(best_match), D

def compute_histograms(image_list, hist_type, hist_isgray, num_bins):

  image_hist = []

  # compute hisgoram for each image and add it at the bottom of image_hist
  # your code here
  for img in image_list:
    img_color = np.array(Image.open(img))
    img = img_color.astype('double')

    if hist_isgray:
      img = rgb2gray(img_color.astype('double'))
    hist = histogram_module.get_hist_by_name(img, num_bins, hist_type)
    if len(hist) == 2 and len(hist[0]) > 1:
      hist = hist[0]
    image_hist.append(hist)

  return image_hist

#
# for each image file from 'query_images' find and visualize the 5 nearest images from 'model_image'.
#
# note: use the previously implemented function 'find_best_match'
# note: use subplot command to show all the images in the same Python figure, one row per query image
#

def show_neighbors(model_images, query_images, dist_type, hist_type, num_bins):

  fig=plt.figure(figsize=(3, 6))

  num_nearest = 5  # show the top-5 neighbors

  # your code here
  best_match, D = find_best_match(model_images, query_images, dist_type, hist_type, num_bins)
  i=1
  for qid in range(len(query_images)):
    model_ids = np.argsort(D[:,qid])[:5]
    img = query_images[qid]
    i = plot_image(img, i, fig)
    for mid in model_ids:
      img = model_images[mid]
      i = plot_image(img, i, fig)
  plt.show()

# Plot images
def plot_image(img, i, fig):
  fig.add_subplot(3, 6, i)
  img_color = np.array(Image.open(img))
  plt.imshow(img_color)
  i=i+1
  return i





