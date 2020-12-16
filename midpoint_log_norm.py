class MidpointLogNorm(colors.SymLogNorm):
    """
    Extended version of the Matplotlib SymLogNorm that allows you to specify a midpoint that will
    be set as the neutral/middle color. It also does a better job centering the midpoint even if 
    the midpoint you want is zero; SymLogNorm gives a color scale very slightly non-centered 
    at zero if zero isn't the median of your data. 

    lin_thres, lin_scale, vmin, vmax: same as SymLogNorm
    
    midpoint: point to set as the center of your data. Will be in white / neutral color based on 
    the colormap you select; but it may not be in the center of the vertical scale. 

    force_symmetric: whether to force the max value on the scale to be the inverse of the min value on
    the scale. If midpoint != 0, this becomes true by default, because the plot will otherwise have
    discontinuities in the color. 
	"""
    def __init__(self, lin_thres, lin_scale, midpoint=0, vmin=None, vmax=None, force_symmetric=False):
        self.midpoint = midpoint
        self.lin_thres = lin_thres
        self.lin_scale = lin_scale
        #fraction of the cmap that the linear component occupies
        self.linear_proportion = (lin_scale / (lin_scale + 1)) * 0.5
        
        if force_symmetric or midpoint != 0:
            dist = max(abs(midpoint - vmin), abs(vmax - midpoint))
            vmin = midpoint - dist
            vmax = midpoint + dist

        #shift SymLogNorm value by the midpoint so that the color scale remains centered around midpoint
        colors.SymLogNorm.__init__(self, lin_thres, lin_scale, vmin - midpoint, vmax - midpoint)

        #bounds for when to use linear scale vs logarithmic
        self.lower = self.midpoint - self.lin_thres
        self.upper = self.midpoint + self.lin_thres
        #used for interpolation with the linear scale
        self.x = [self.lower, self.midpoint, self.upper]
        self.y = [0.5 - self.linear_proportion, 0.5, 0.5 + self.linear_proportion]

    def __get_value__(self, v, log_val):
        #use default from SymLogNorm if out of linear range; else use interpolation
        if v < self.lower or v > self.upper:
            return log_val
        interpol = np.interp(v, self.x, self.y)
        return interpol

    def __call__(self, value, clip=None):
        #shift SymLogNorm value by the midpoint so that the color scale remains centered
        log_val = colors.SymLogNorm.__call__(self, value - self.midpoint)
        out = [0] * len(value)
        for i, v in enumerate(value):
            out[i] = self.__get_value__(v, log_val[i])
        return np.ma.masked_array(out)

