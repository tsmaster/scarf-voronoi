# scarf-voronoi
python code to generate a PNG and TIFF for a voronoi scarf, suitable for knitting on a computer controlled knitting machine

## Requirements
 - Python (tested with 2.7)
 - PIL/Pillow
 
## To Run
```% python scarf.py```

## Algorithm
I use the "Fast Poisson Disk Sampling in Arbitrary Dimensions" algorithm from Robert Bridson https://dl.acm.org/citation.cfm?id=1278807 to generate a set of points that are no closer to each other than 25 pixels. I then walk every pixel of the canvas to see if that pixel is within 4 pixels of another region, or within 4 pixels of the edge of the canvas, in which case, I draw that pixel in a dark color.

