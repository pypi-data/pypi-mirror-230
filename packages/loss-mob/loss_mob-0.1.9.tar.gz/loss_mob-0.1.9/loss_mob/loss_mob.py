# loss_mob/loss_mob.py
# version 0.1.9, 09/07/2023
# import sys
# sys.path.append("loss_mob")
# import loss_mob

import tabulate, numpy, cytoolz, operator
from scipy.stats import spearmanr, variation
from dcor import distance_correlation as distancer
from sklearn.isotonic import IsotonicRegression as isoreg
from sklearn.cluster import KMeans as kmeans
from sklearn.ensemble import HistGradientBoostingRegressor as gbmreg
from sklearn.datasets import fetch_openml

########## 01. qcut() ##########

def qcut(x, n):
  """
  It is an utility function to discretizes a numeric vector into n pieces 
  based on quantiles and not directly callable by end-users.
  Parameters:
    x : A numeric vector.
    n : An integer indicating the number of categories to discretize.
  Returns:
    A list of numeric values to divide the vector x into n categories.
  """

  _q = numpy.linspace(0, 100, n, endpoint = False)[1:]
  _x = [_ for _ in x if not numpy.isnan(_)]
  return(numpy.unique(numpy.percentile(_x, _q, method = "lower")))


########## 02. manual_bin() ##########

def manual_bin(x, y, cuts):
  """
  It is an utility function to discretize the x vector and summarize over 
  the y vector based on the discretization result.
  Parameters:
    x    : A numeric vector to discretize without missing values
    y    : A numeric vector with the same length of x
    cuts : A list of numeric values as cut points to discretize x.
  Returns:
    A list of dictionaries for the binning outcome.
  """

  chk_len(x, y)

  _c = sorted([_ for _ in set(cuts)] + [numpy.NINF, numpy.PINF])
  _g = numpy.searchsorted(_c, x).tolist()

  _l1 = sorted(zip(_g, x, y), key = lambda x: x[0])

  _l2 = zip(set(_g), [[l for l in _l1 if l[0] == g] for g in set(_g)])

  return(sorted([dict(zip(["bin", "freq", "miss", "ysum", "minx", "maxx"],
                          [_1, len(_2), 0,
                           sum([_[2] for _ in _2]),
                           min([_[1] for _ in _2]),
                           max([_[1] for _ in _2])])) for _1, _2 in _l2],
                key = lambda x: x["bin"]))


########## 03. miss_bin() ##########

def miss_bin(y):
  """
  It is an utility function to summarize the y vector.
  Parameters:
    y : A numeric vector.
  Returns:
    A dictionary.
  """

  return({"bin": 0, "freq": len([_ for _ in y]), "miss": len([_ for _ in y]),
          "ysum": sum([_ for _ in y]), "minx": numpy.nan, "maxx": numpy.nan})


########## 04. add_miss() ##########

def add_miss(d, l):
  """
  It is an utility function to append the missing value category, if any, to 
  the binning outcome and not callable by end-users.
  Parameters:
    d : A list with lists generated by input vectors of binning functions.
    l : A list of dicts to append.
  Returns:
    A list of dicts.
  """

  _l = l[:]

  if len([_ for _ in d if _[2] == 0]) > 0:
    _m = miss_bin([_[1] for _ in d if _[2] == 0])
    if _m["ysum"] == 0:
      for _ in ['freq', 'miss', 'ysum']:
        _l[0][_]  = _l[0][_]  + _m[_]
    else:
      _l.append(_m)

  return(_l)


########## 05. gen_newx() ##########

def gen_newx(x):
  """
  It is an utility function to generate the variable transformation based on
  the binning outcome and not callable by end-users.
  Parameters:
    x : A list of dictionaries for the binning outcome.
  Returns:
    A list of dictionaries with additional keys to the input.
  """

  _freq = sum(_["freq"] for _ in x)
  _ysum = sum(_["ysum"] for _ in x)

  return(sorted([{**_,
                  "yavg": round(_["ysum"] / _["freq"], 8),
                  "newx": round(numpy.log((_["ysum"] / _ysum) / (_["freq"] / _freq)), 8)
                 } for _ in x], key = lambda _x: _x["bin"]))


########## 06. gen_rule() ##########

def gen_rule(tbl, pts):
  """
  It is an utility function to generate binning rules based on the binning 
  outcome table and the list of cut points.
  Parameters:
    tbl : A intermediate table of the binning outcome
    pts : A list cut points for the binning
  Returns:
    A list of dictionaries with binning rules
  """

  for _ in tbl:
    if _["bin"] == 0:
      _["rule"] = "numpy.isnan($X$)"
    elif _["bin"] == len(pts) + 1:
      if _["miss"] == 0:
        _["rule"] = "$X$ > " + str(pts[-1])
      else:
        _["rule"] = "$X$ > " + str(pts[-1]) + " or numpy.isnan($X$)"
    elif _["bin"] == 1:
      if _["miss"] == 0:
        _["rule"] = "$X$ <= " + str(pts[0])
      else:
        _["rule"] = "$X$ <= " + str(pts[0]) + " or numpy.isnan($X$)"
    else:
        _["rule"] = "$X$ > " + str(pts[_["bin"] - 2]) + " and $X$ <= " + str(pts[_["bin"] - 1])

  _sel = ["bin", "freq", "miss", "ysum", "yavg", "newx", "rule"]
  return([{k: _[k] for k in _sel} for _ in tbl])


########## 07.1 cal_newx() ##########

def cal_newx(x, b):
  """
  It applies the binning transformation to a numeric vector.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    b : An object containing the binning outcome.
  Returns:
    A list of dictionaries with three keys
  """

  _cut = sorted([_ for _ in b['cut']] + [numpy.PINF, numpy.NINF])
  _dat = [[_1[0], _1[1], _2] for _1, _2 in zip(enumerate(x), ~numpy.isnan(x))]

  _m1 = [_[:2] for _ in _dat if _[2] == 0]
  _l1 = [_[:2] for _ in _dat if _[2] == 1]

  _l2 = [[*_1, _2] for _1, _2 in zip(_l1, numpy.searchsorted(_cut, [_[1] for _ in _l1]).tolist())]

  flatten = lambda l: [item for subl in l for item in subl]

  _l3 = flatten([[[*l, _['newx']] for l in _l2 if l[2] == _['bin']] for _ in b['tbl'] if _['bin'] > 0])

  if len(_m1) > 0:
    if len([_ for _ in b['tbl'] if _['miss'] > 0]) > 0:
      _m2 = [l + [_['bin'] for _ in b['tbl'] if _['miss'] > 0]
               + [_['newx'] for _ in b['tbl'] if _['miss'] > 0] for l in _m1]
    else:
      _m2 = [l + [0, 0] for l in _m1]
    _l3.extend(_m2)

  _key = ['x', 'bin', 'newx']
  return(list(dict(zip(_key, _[1:])) for _ in sorted(_l3, key = lambda x: x[0])))


########## 07.2 chk_newx() ##########

def chk_newx(l):
  """
  It verifies the transformation generated from the cal_newx() function.
  Parameters:
    l : A list of dictionaries directly generated by cal_newx() function.
  """

  tabulate.PRESERVE_WHITESPACE = True

  _cn = len(l)
  _l1 = sorted([{"bin" : _[0][0], "newx": _[0][1], "freq": len(_[1]),
                 "dist": format(len(_[1]) / _cn, ".4%").rjust(10),
                 "xrng": (str(numpy.min([_g["x"] for _g in _[1]])) + " <==> " +
                          str(numpy.max([_g["x"] for _g in _[1]]))).rjust(40)
                } for _ in cytoolz.groupby(['bin', 'newx'], l).items()],
               key = lambda x: x["bin"])

  print(tabulate.tabulate(_l1, headers = "keys", tablefmt = "github",
                          colalign = ["center"] + ["right"] * 2 + ["center"] * 2,
                          floatfmt = (".0f", ".8f", ".0f")))


########## 08.1 mi_score() ##########

def mi_score(x, y):
  """
  It calculates the Mutual Information (MI) score between x and y.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector, e.g. list, numpy array, or pandas series.
  Returns:
    The mutual information score.
  """
  
  chk_len(x, y)

  _dt = [_ for _ in zip(x, y) if ~numpy.isnan(_[0]) and ~numpy.isnan(_[1])]
  _cn = len(_dt)

  _l1 = [{"x": i[0][0], "y": i[0][1], "pxy": len(i[1]) / _cn}
         for i in list(cytoolz.groupby([0, 1], _dt).items())]

  _lx = [{"x": i[0], "px": sum([_["pxy"] for _ in i[1]])}
         for i in list(cytoolz.groupby("x", _l1).items())]

  _ly = [{"y": i[0], "py": sum([_["pxy"] for _ in i[1]])}
         for i in list(cytoolz.groupby("y", _l1).items())]

  _l2 = list(dict(_l, **_r) for _l, _r in 
             cytoolz.join(operator.itemgetter("x"), _l1, operator.itemgetter("x"), _lx))

  _l3 = list(dict(_l, **_r) for _l, _r in 
             cytoolz.join(operator.itemgetter("y"), _l2, operator.itemgetter("y"), _ly))

  return(sum([_["pxy"] * numpy.log(_["pxy"] / (_["px"] * _["py"])) for _ in _l3]))


########## 08.2 screen() ##########

def screen(x, y):
  """
  It provides spearman and distance correlations between x and y.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector, e.g. list, numpy array, or pandas series.
  Returns:
    A dictionary with the statistical summary.
  """

  chk_len(x, y)

  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x = numpy.array([_[0] for _ in _data if _[2] == 1]).astype(float)
  _y = numpy.array([_[1] for _ in _data if _[2] == 1]).astype(float)

  return({"total records"           : len(_data),
          "nonmissing records"      : len(_x),
          "missing percent"         : round(1 - len(_x) / len(_data), 8),
          "unique value count"      : len(numpy.unique(_x)),
          "coefficient of variation": round(variation(_x), 8),
          "spearman correlation"    : round(spearmanr(_x, _y)[0], 8),
          "distance correlation"    : round(distancer(_x, _y), 8)})


########## 08.3 gini() ##########

def gini(b):
  """
  It calculates the gini-coefficient between x and y based on the binning
  outcome.
  Parameters:
    b : An object containing the binning outcome.
  Returns:
    The gini-coefficient value.
  """

  fsum = sum([_["freq"] for _ in b["tbl"]])
  ysum = sum([_["ysum"] for _ in b["tbl"]])

  _l1 = sorted([[_["yavg"], _["freq"] / fsum, _["ysum"] / ysum] for _ in b["tbl"]],
               key = lambda k: k[0])

  cumsum = lambda _l: [sum(_l[0:(i + 1)]) for i in range(len(_l))]

  ycum = cumsum([_[2] for _ in _l1])

  _l2 = [[*_[0], _[1], _[2], (_[1] + _[2]) * _[0][1] / 2]
         for _ in zip(_l1, [0] + ycum[:-1], ycum)]

  return((0.5 - sum([_[5] for _ in _l2])) * 2)


########## 08.4 get_mtpl() ##########

def get_mtpl():
  """
  It extracts French Motor Third-Part Liability Claims dataset from the OpenML 
  data portal. See https://github.com/dutangc/CASdatasets for details.
  Returns:
    A dict with 14 keys below:
      idpol      : The policy ID;
      claimnb    : The number of claims during the exposure period;
      exposure   : The period of exposure for a policy, in years;
      area       : The density value of the city community where the car driver
                   lives in: from "A" for rural area to "F" for urban center;
      vehpower   : The power of the car (ordered values);
      vehage     : The vehicle age, in years;
      drivage    : The driver age, in years;
      bonusmalus : Bonus / malus, between 50 and 350: < 100 means bonus,
                   > 100 means malus in France;
      vehbrand   : The car brand (unknown categories)
      vehgas     : The car gas, Diesel or regular.
      density    : The density of inhabitants (number of inhabitants per 
                   square-kilometer) of the city where the driver lives in;
      region     : The policy region in France;
      claimamount: The cost of the claim;
      purepremium: The Pure Premium that is the expected total claim amount 
                   per unit of exposure for each policyholder.
  """

  _f1 = fetch_openml(data_id = 41214, as_frame = True, parser = "pandas").data.to_dict(orient = 'records')
  _f2 = sorted([{**_, "IDpol": int(_["IDpol"]), "VehGas": _["VehGas"].replace("'", "")} for _ in _f1], 
               key = lambda x: x["IDpol"])

  _s1 = fetch_openml(data_id = 41215, as_frame = True, parser = "pandas").data.to_dict(orient = 'records')
  _s2 = sorted([{"IDpol": _g[0], "ClaimAmount": round(sum([_["ClaimAmount"] for _ in _g[1]]), 8)}
                for _g in cytoolz.groupby("IDpol", _s1).items()], key = lambda x: x["IDpol"])

  _p1 = list(dict(_l, **_r) for _l, _r in
             cytoolz.join(operator.itemgetter("IDpol"), _f2, operator.itemgetter("IDpol"), _s2, 
                          right_default = {"ClaimAmount": 0}))
  _p2 = [{**_, "PurePremium": round(_["ClaimAmount"] / _["Exposure"], 4)} for _ in _p1]

  return(dict((k.lower(), [_[k] for _ in _p2]) for k in _p2[0].keys()))


########## 09.1 view_bin() ##########

def view_bin(x):
  """
  It displays the binning outcome generated from a binning function.
  Parameters:
    x : An object containing the binning outcome.
  """

  tabulate.PRESERVE_WHITESPACE = True

  _sel = ["bin", "freq", "miss", "ysum", "yavg", "newx"]
  _tbl = [{**(lambda v: {k: v[k] for k in _sel})(_), "rule": _["rule"].ljust(50)} 
          for _ in x["tbl"]]

  print(tabulate.tabulate(_tbl, headers = "keys", tablefmt = "github",
                          colalign = ["center"] + ["right"] * (len(_sel) - 1) + ["center"],
                          floatfmt = (".0f", ".0f", ".0f", ".4f", ".4f", ".8f")))


########## 09.2 head() ##########

def head(l, n = 3):
  """
  It shows first n (3 by default) items in a sequence.
  Parameters:
    l : A list.
    n : A non-zero integer.
  """

  for _ in range(n):
    print(l[_])


########## 09.3 chk_neg(y) ##########

def chk_neg(y):
  """
  It checks if there is any negative value in the Y vector 
  and not supposed to be called by end-users.
  Parameters:
    y : A numeric vector, e.g. list, numpy array, or pandas series.
  """

  if len([_ for _ in y if _ < 0]) > 0:
    raise ValueError("Values in the Y vector can't be negative.")


########## 09.4 chk_len(y) ##########

def chk_len(x, y):
  """
  It checks if len(X) is different from len(Y) and not callable by end-users.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector, e.g. list, numpy array, or pandas series.
  """

  if len(x) != len(y):
    raise ValueError("len(X) is different from len(Y).")


########## 11. qtl_bin() ##########

def qtl_bin(x, y):
  """
  It discretizes the x vector based on percentiles and summarizes
  over the y vector to derive the variable transformation.
  Parameters:
    x : A numeric vector , e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """
  
  chk_neg(y)
  chk_len(x, y)

  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  _n = numpy.arange(2, max(3, min(50, len(set(_x)) - 1)))
  _p = set(tuple(qcut(_x, _)) for _ in _n)

  _l1 = [[_, manual_bin(_x, _y, _)] for _ in _p]

  _l2 = [[l[0],
          min([_["ysum"] / _["freq"] for _ in l[1]]),
          spearmanr([_["bin"] for _ in l[1]], [_["ysum"] / _["freq"] for _ in l[1]])[0]
         ] for l in _l1]

  _l3 = [l[0] for l in sorted(_l2, key = lambda x: -len(x[0]))
         if numpy.abs(round(l[2], 8)) == 1 and round(l[1], 8) > 0][0]

  _l4 = sorted(*[l[1] for l in _l1 if l[0] == _l3], key = lambda x: x["ysum"] / x["freq"])

  _l5 = add_miss(_data, _l4)

  return({"cut": _l3, "tbl": gen_rule(gen_newx(_l5), _l3)})


########## 12. iso_bin() ##########

def iso_bin(x, y):
  """
  It discretizes the x vector based on the isotonic regression and summarizes
  over the y vector to derive the variable transformation.
  Parameters:
    x : A numeric vector , e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """

  chk_neg(y)
  chk_len(x, y)

  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  _f = isoreg(increasing = "auto").fit_transform(_x, _y)

  _l1 = sorted(list(zip(_f, _x, _y)), key = lambda x: x[0])

  _l2 = [[l for l in _l1 if l[0] == f] for f in sorted(set(_f))]

  _l3 = [[*set(_[0] for _ in l),
          max(_[1] for _ in l),
          numpy.mean([_[2] for _ in l]),
          len(list(_[2] for _ in l))] for l in _l2]

  _c = sorted([_[1] for _ in [l for l in _l3 if l[2] > 0 and l[3] >= 10]])
  _p = _c[:-1] if len(_c) > 1 else _c[:]

  _l4 = sorted(manual_bin(_x, _y, _p), key = lambda x: x["ysum"] / x["freq"])

  _l5 = add_miss(_data, _l4)

  return({"cut": _p, "tbl": gen_rule(gen_newx(_l5), _p)})


########## 13. gbm_bin() ##########

def gbm_bin(x, y):
  """
  It discretizes the x vector based on the gradient boosting machine and
  summarizes over the y vector to derive the variable transformation.
  Parameters:
    x : A numeric vector , e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """

  chk_neg(y)
  chk_len(x, y)
  
  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  _c = 1 if spearmanr(_x, _y)[0] > 0 else -1
  _m = gbmreg(min_samples_leaf = 10, monotonic_cst = [_c], random_state = 1,
              early_stopping = False, validation_fraction = None, 
             ).fit(numpy.reshape(_x, [-1, 1]), _y)
  _f = _m.predict(numpy.reshape(_x, [-1, 1]))

  _l1 = sorted(list(zip(_f, _x, _y)), key = lambda x: x[0])

  _l2 = [[l for l in _l1 if l[0] == f] for f in sorted(set(_f))]

  _l3 = [[*set(_[0] for _ in l),
          max(_[1] for _ in l),
          numpy.mean([_[2] for _ in l]),
          len(list(_[2] for _ in l))] for l in _l2]

  _c = sorted([_[1] for _ in [l for l in _l3 if l[2] > 0 and l[3] >= 10]])

  _p = _c[:-1] if len(_c) > 1 else _c[:]

  _l4 = sorted(manual_bin(_x, _y, _p), key = lambda x: x["ysum"] / x["freq"])

  _l5 = add_miss(_data, _l4)

  return({"cut": _p, "tbl": gen_rule(gen_newx(_l5), _p)})


########## 14. val_bin() ##########

def val_bin(x, y):
  """
  It discretizes the x vector based on unique values of x and summarizes over
  the y vector to derive the variable transformaton.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """

  chk_neg(y)
  chk_len(x, y)
  
  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  _n = numpy.arange(2, max(3, min(50, len(set(_x)) - 1)))

  _m = [[numpy.median([_[0] for _ in _data if _[2] == 1 and _[1] > 0])],
        [numpy.median([_[0] for _ in _data if _[2] == 1])]]

  _p = list(set(tuple(qcut(set(_x), _)) for _ in _n)) + _m

  _l1 = [[_, manual_bin(_x, _y, _)] for _ in _p]

  _l2 = [[l[0],
          min([_["ysum"] / _["freq"] for _ in l[1]]),
          spearmanr([_["bin"] for _ in l[1]], [_["ysum"] / _["freq"] for _ in l[1]])[0]
         ] for l in _l1]

  _l3 = [l[0] for l in sorted(_l2, key = lambda x: -len(x[0]))
         if numpy.abs(round(l[2], 8)) == 1 and round(l[1], 8) > 0][0]

  _l4 = sorted(*[l[1] for l in _l1 if l[0] == _l3], key = lambda x: x["ysum"] / x["freq"])

  _l5 = add_miss(_data, _l4)

  return({"cut": _l3, "tbl": gen_rule(gen_newx(_l5), _l3)})


########## 15. kmn_bin() ##########

def kmn_bin(x, y):
  """
  It discretizes the x vector based on the kmeans clustering and summarizes over 
  the y vector to derive the variable transformation.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """

  chk_neg(y)
  chk_len(x, y)

  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  _n = numpy.arange(2, max(3, min(50, len(set(_x)) - 1)))

  _m = [[numpy.median([_[0] for _ in _data if _[2] == 1 and _[1] > 0])],
        [numpy.median([_[0] for _ in _data if _[2] == 1])]]

  _c1 = [kmeans(n_clusters = _, random_state = 1, n_init = 'auto').fit(numpy.reshape(_x, [-1, 1])).labels_ for _ in _n]

  _c2 = [sorted(_l, key = lambda x: x[0]) for _l in [list(zip(_, _x)) for _ in _c1]]

  group = lambda x: [[_l for _l in x if _l[0] == _k] for _k in set([_[0] for _ in x])]

  upper = lambda x: sorted([max([_2[1] for _2 in _1]) for _1 in x])

  _c3 = list(set(tuple(upper(_2)[:-1]) for _2 in [group(_1) for _1 in _c2])) + _m

  _l1 = [[_, manual_bin(_x, _y, _)] for _ in _c3]

  _l2 = [[l[0],
          min([_["ysum"] / _["freq"] for _ in l[1]]),
          spearmanr([_["bin"] for _ in l[1]], [_["ysum"] / _["freq"] for _ in l[1]])[0]
         ] for l in _l1]

  _l3 = [l[0] for l in sorted(_l2, key = lambda x: -len(x[0]))
         if numpy.abs(round(l[2], 8)) == 1 and round(l[1], 8) > 0][0]

  _l4 = sorted(*[l[1] for l in _l1 if l[0] == _l3], key = lambda x: x["ysum"] / x["freq"])

  _l5 = add_miss(_data, _l4)

  return({"cut": _l3, "tbl": gen_rule(gen_newx(_l5), _l3)})


########## 16. los_bin() ##########

def los_bin(x, y):
  """
  It discretizes the x vector based on percentiles and summarizes over the
  y vector with y > 0, i.e. nonzero loss, to derive the transformation.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """

  chk_neg(y)
  chk_len(x, y)

  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  _n = numpy.arange(2, max(3, min(50, len(set([_[0] for _ in _data if _[1] > 0 and _[2] == 1])) - 1)))

  _p = set(tuple(qcut([_[0] for _ in _data if _[1] > 0 and _[2] == 1], _)) for _ in _n)

  _l1 = [[_, manual_bin(_x, _y, _)] for _ in _p]

  _l2 = [[l[0],
          min([_["ysum"] / _["freq"] for _ in l[1]]),
          spearmanr([_["bin"] for _ in l[1]], [_["ysum"] / _["freq"] for _ in l[1]])[0]
         ] for l in _l1]

  _l3 = [l[0] for l in sorted(_l2, key = lambda x: -len(x[0]))
         if numpy.abs(round(l[2], 8)) == 1 and round(l[1], 8) > 0][0]

  _l4 = sorted(*[l[1] for l in _l1 if l[0] == _l3], key = lambda x: x["ysum"] / x["freq"])

  _l5 = add_miss(_data, _l4)

  return({"cut": _l3, "tbl": gen_rule(gen_newx(_l5), _l3)})


########## 17. rng_bin() ##########

def rng_bin(x, y):
  """
  It discretizes the x vector based on the equal-width range of x and 
  summarizes over the y vector to derive the variable transformaton.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """

  chk_neg(y)
  chk_len(x, y)

  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  minx = min(_x)
  maxx = max(_x)

  _n = numpy.arange(2, max(3, min(50, len(set(_x)) - 1)))

  _p = [list(numpy.round(numpy.linspace(minx, maxx, _, endpoint = False)[1:], 8)) for _ in _n]

  _l1 = [[_, manual_bin(_x, _y, _)] for _ in _p]

  _l2 = [[l[0],
          min([_["ysum"] / _["freq"] for _ in l[1]]),
          spearmanr([_["bin"] for _ in l[1]], [_["ysum"] / _["freq"] for _ in l[1]])[0]
         ] for l in _l1]

  _l3 = [l[0] for l in sorted(_l2, key = lambda x: -len(x[0]))
         if numpy.abs(round(l[2], 8)) == 1 and round(l[1], 8) > 0][0]

  _l4 = sorted(*[l[1] for l in _l1 if l[0] == _l3], key = lambda x: x["ysum"] / x["freq"])

  _l5 = add_miss(_data, _l4)

  return({"cut": _l3, "tbl": gen_rule(gen_newx(_l5), _l3)})


########## 18. cus_bin() ##########

def cus_bin(x, y, c):
  """
  It discretizes the x vector based on pre-determined cut points and
  summarizes over the y vector to derive the variable transformation.
  Parameters:
    x : A numeric vector, e.g. list, numpy array, or pandas series.
    y : A numeric vector of loss outcomes with the same length of x.
    c : A list of numeric values, as pre-defined cut points.
  Returns:
    A dictionary with two keys:
      "cut" : A numeric vector with cut points applied to the x vector.
      "tbl" : A list of dictionaries summarizing the binning outcome.
  """

  chk_neg(y)
  chk_len(x, y)

  _data = [_ for _ in zip(x, y, ~numpy.isnan(x))]
  _x, _y = [[_[i] for _ in _data if _[2] == 1] for i in [0, 1]]

  _l1 = sorted(manual_bin(_x, _y, c), key = lambda x: x["bin"])

  _l2 = add_miss(_data, _l1)

  return({"cut": c, "tbl": gen_rule(gen_newx(_l2), c)})

