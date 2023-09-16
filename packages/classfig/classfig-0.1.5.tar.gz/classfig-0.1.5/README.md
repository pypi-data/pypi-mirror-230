# classfig
Comfortable figure handling in Python3 / Matplotlib

written by Fabian Stutzki, fast@fast-apps.de

licensed under MIT

## Usage
The package has to be imported:

```python
from classfig import classfig
```

A very simple example is:

```python
fig = classfig()
fig.plot()
fig.show()
```

classfig allows for more complex behavior with multiple subplots, legend, grid and saving to multiple files at once.

```python
fig = classfig('PPT',nrows=2) # create figure
fig.plot([1,2,3,1,2,3,4,1,1]) # plot first data set
fig.title('First data set') # set title for subplot
fig.subplot() # set focus to next subplot/axis
fig.plot([0,1,2,3,4],[0,1,1,2,3],label="random") # plot second data set
fig.legend() # generate legend
fig.grid() # show translucent grid to highlight major ticks
fig.xlabel('Data') # create xlabel for second axis
fig.save('debug_fig1.png','pdf') # save figure to png and pdf
```

