#!/usr/bin/env python3
"""v18: +10 math11 and +7 math12 grade-pure numericals, and removal of class-9/10 templates that leaked into the specs (math12: pythag, pct_change, circle_area,
sphere_vol, arc; math11: pythag, pct_change). Idempotent; updates engine/param_templates.json, docs/model/templates.json, packs/pack_specs.json.
Unit names are the real math11/math12 syllabus_graph unit names."""
import json, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def T(id, unit, kw, vars_, stem, ans, wrong, law, lawname, sol, u="", sig=3, cond="ans>0"):
    return dict(id=id, dom="maths", lv="H", unit=unit, kw=kw, vars=vars_, derived="", stem=stem, ans=ans, u=u, wrong=wrong, law=law, lawname=lawname, sol=sol, sig=sig, cond=cond)


M11 = [
    T("m11_cmod", "Complex Numbers", ["modulus", "complex", "number", "absolute"], ["a=[3,5,8,6,7]", "b=[4,12,15,8,24]"], r"Find the modulus of the complex number $z = @a@ + @b@i$.", "sqrt(a**2+b**2)",
      ["a+b", "a**2+b**2", "sqrt(a*b)", "sqrt(abs(a**2-b**2))"], r"$|a+bi| = \sqrt{a^2+b^2}$.", "the modulus of a complex number", [r"$|z| = \sqrt{@a@^2+@b@^2}$", r"$|z| = @ans@$"]),
    T("m11_cmul", "Complex Numbers", ["product", "real", "part", "complex", "multiplication"], ["a=[1,2,3,4]", "b=[1,2,5]", "c=[2,3,4]", "d=[3,4,6]"],
      r"Find the real part of $(@a@ + @b@i)(@c@ + @d@i)$.", "a*c-b*d", ["a*c+b*d", "a*d+b*c", "a*c", "(a+c)*(b+d)"], r"$(a+bi)(c+di) = (ac-bd) + (ad+bc)i$.", "complex multiplication",
      [r"$\text{Re} = @a@\times@c@ - @b@\times@d@$", r"$\text{Re} = @ans@$"], cond="a*c-b*d!=0 and a*c-b*d!=a*d+b*c"),
    T("m11_sd", "Measures of Dispersion", ["standard", "deviation", "mean", "squares", "variance"], ["ms=[26,29,34,41,50]", "m=[4,5]"],
      r"For a data set the mean of the squares of the observations is $@ms@$ and the mean of the observations is $@m@$. Find the standard deviation.", "sqrt(ms-m**2)", ["sqrt(ms)-m", "ms-m**2", "sqrt(ms+m**2)", "sqrt(ms)"],
      r"$\sigma^2 = \dfrac{\sum x^2}{n} - \left(\dfrac{\sum x}{n}\right)^2$.", "the variance formula", [r"$\sigma = \sqrt{@ms@ - @m@^2}$", r"$\sigma = @ans@$"], cond="ms>m**2"),
    T("m11_cprob", "Probability", ["conditional", "probability", "events", "intersection"], ["pab=[0.1,0.2,0.3]", "pb=[0.4,0.5,0.6]"],
      r"If $P(A\cap B) = @pab@$ and $P(B) = @pb@$, find $P(A\mid B)$.", "pab/pb", ["pb/pab", "pab*pb", "pab/(1-pb)", "pab+pb"], r"$P(A\mid B) = \dfrac{P(A\cap B)}{P(B)}$.", "conditional probability",
      [r"$P(A\mid B) = \dfrac{@pab@}{@pb@}$", r"$P(A\mid B) = @ans@$"]),
    T("m11_line_dist", "Straight Line", ["distance", "point", "line", "perpendicular"], ["a=[3,4,5]", "b=[4,3,12]", "x1=[1,2,3]", "y1=[1,2,5]", "c=[-5,-10,10]"],
      r"Find the perpendicular distance of the point $(@x1@, @y1@)$ from the line $@a@x + @b@y + (@c@) = 0$.", "abs(a*x1+b*y1+c)/sqrt(a**2+b**2)",
      ["(a*x1+b*y1+c)/(a+b)", "abs(a*x1+b*y1+c)", "abs(a*x1+b*y1+c)/(a**2+b**2)", "abs(a*x1+b*y1)/sqrt(a**2+b**2)"], r"$d = \dfrac{|ax_1+by_1+c|}{\sqrt{a^2+b^2}}$.", "the distance of a point from a line",
      [r"$d = \dfrac{|@a@\times@x1@ + @b@\times@y1@ + (@c@)|}{\sqrt{@a@^2+@b@^2}}$", r"$d = @ans@$"], cond="a*x1+b*y1+c!=0 and c!=0"),
    T("m11_angle_lines", "Straight Line", ["angle", "between", "lines", "slopes"], ["m1=[2,3,4,5]", "m2=[1,0.5,0.25]"],
      r"Find the acute angle (in degrees) between two lines of slopes $@m1@$ and $@m2@$.", "atan(abs((m1-m2)/(1+m1*m2)))*180/pi",
      ["atan(abs((m1+m2)/(1-m1*m2)))*180/pi", "atan(abs(m1-m2))*180/pi", "atan(abs((m1-m2)*(1+m1*m2)))*180/pi", "atan(m1*m2)*180/pi"], r"$\tan\theta = \left|\dfrac{m_1-m_2}{1+m_1m_2}\right|$.", "the angle between two lines",
      [r"$\tan\theta = \left|\dfrac{@m1@-@m2@}{1+@m1@\times@m2@}\right|$", r"$\theta = @ans@^{\circ}$"], u=r"^{\circ}"),
    T("m11_vec_mag", "Vectors", ["magnitude", "vector", "length", "components"], ["x=[1,2,3,4,6]", "y=[2,3,4,5,7]", "z=[2,6,5,12,6]"],
      r"Find the magnitude of the vector $\vec{a} = @x@\hat{i} + @y@\hat{j} + @z@\hat{k}$.", "sqrt(x**2+y**2+z**2)", ["x+y+z", "x**2+y**2+z**2", "sqrt(x*y*z)", "sqrt(x**2+y**2)"],
      r"$|\vec{a}| = \sqrt{x^2+y^2+z^2}$.", "the magnitude of a vector", [r"$|\vec{a}| = \sqrt{@x@^2+@y@^2+@z@^2}$", r"$|\vec{a}| = @ans@$"]),
    T("m11_dist3d", "Coordinates in Space", ["distance", "points", "space", "three", "dimensions"], ["x=[4,5,7,9]", "y=[6,2,8,4]", "z=[3,9,6,15]"],
      r"Find the distance between the points $P(1, 2, 3)$ and $Q(@x@, @y@, @z@)$.", "sqrt((x-1)**2+(y-2)**2+(z-3)**2)", ["(x-1)+(y-2)+(z-3)", "(x-1)**2+(y-2)**2+(z-3)**2", "sqrt(x**2+y**2+z**2)", "sqrt((x+1)**2+(y+2)**2+(z+3)**2)"],
      r"$PQ = \sqrt{(x_2-x_1)^2+(y_2-y_1)^2+(z_2-z_1)^2}$.", "the 3-D distance formula", [r"$PQ = \sqrt{(@x@-1)^2+(@y@-2)^2+(@z@-3)^2}$", r"$PQ = @ans@$"], cond="ans>0 and (x-1)+(y-2)+(z-3)!=ans"),
    T("m11_gp_sum", "Sequence and Series", ["geometric", "series", "sum", "terms"], ["a=[1,2,3,5]", "r=[2,3]", "n=[3,4,5,6]"],
      r"Find the sum of the first $@n@$ terms of the geometric series with first term $@a@$ and common ratio $@r@$.", "a*(r**n-1)/(r-1)", ["a*r**n", "a*(r**n-1)", "a*(r**(n-1)-1)/(r-1)", "a*r**(n-1)"],
      r"$S_n = \dfrac{a(r^n-1)}{r-1}$ for $r>1$.", "the sum of a GP", [r"$S_n = \dfrac{@a@(@r@^{@n@}-1)}{@r@-1}$", r"$S_n = @ans@$"]),
    T("m11_sum_cubes", "Sequence and Series", ["sum", "cubes", "natural", "numbers"], ["n=[4,5,6,8,10]"], r"Find $1^3 + 2^3 + \cdots + @n@^3$.", "(n*(n+1)/2)**2",
      ["n**2*(n+1)**2", "n*(n+1)*(2*n+1)/6", "(n*(n+1))**2/2", "n*(n+1)/2"], r"$\sum n^3 = \left[\dfrac{n(n+1)}{2}\right]^2$.", "the sum of cubes", [r"$\left[\dfrac{@n@(@n@+1)}{2}\right]^2$", r"Sum $= @ans@$"]),
]
M12 = [
    T("m12_ellipse_e", "Conic Sections", ["ellipse", "eccentricity", "axes", "semi"], ["a=[5,10,13,17]", "b=[3,4,6,8]"],
      r"Find the eccentricity of the ellipse $\dfrac{x^2}{@a@^2} + \dfrac{y^2}{@b@^2} = 1$.", "sqrt(1-b**2/a**2)", ["sqrt(a**2-b**2)", "b/a", "1-b**2/a**2", "sqrt(a**2+b**2)/a"], r"$e = \sqrt{1-\dfrac{b^2}{a^2}}$ for $a>b$.", "the eccentricity of an ellipse",
      [r"$e = \sqrt{1-\dfrac{@b@^2}{@a@^2}}$", r"$e = @ans@$"], cond="b<a"),
    T("m12_parab_focus", "Conic Sections", ["parabola", "focus", "latus", "rectum"], ["k=[8,12,16,20,24]"], r"Find the $x$-coordinate of the focus of the parabola $y^2 = @k@x$.", "k/4", ["k/2", "k", "4*k", "k/8"],
      r"Compare with $y^2 = 4ax$: the focus is $(a, 0)$ with $4a = k$.", "the focus of a parabola", [r"$4a = @k@ \Rightarrow a = \dfrac{@k@}{4}$", r"Focus: $x = @ans@$"]),
    T("m12_binom_term", "Binomial Theorem", ["binomial", "coefficient", "expansion", "term"], ["n=[5,6,7,8]", "r=[2,3]", "a=[2,3]"],
      r"Find the coefficient of $x^{@r@}$ in the expansion of $(1 + @a@x)^{@n@}$.", "comb(n,r)*a**r", ["comb(n,r)", "comb(n,r)*a", "perm(n,r)*a**r", "comb(n,r)*r**a"], r"$T_{r+1} = {}^nC_r\,(ax)^r$.", "the general term of a binomial expansion",
      [r"${}^{@n@}C_{@r@}\times@a@^{@r@}$", r"Coefficient $= @ans@$"]),
    T("m12_demoivre", "Complex Numbers", ["demoivre", "theorem", "power", "polar", "complex"], ["th=[10,15,20,25,40]", "n=[3,6,9]"],
      r"Using De Moivre's theorem, find the real part of $(\cos @th@^\circ + i\sin @th@^\circ)^{@n@}$.", "cos(rad(n*th))", ["cos(rad(th))**n", "n*cos(rad(th))", "sin(rad(n*th))", "cos(rad(th))/n"],
      r"$(\cos\theta + i\sin\theta)^n = \cos n\theta + i\sin n\theta$.", "De Moivre's theorem", [r"$\cos(@n@\times@th@^\circ)$", r"$\text{Re} = @ans@$"], cond="abs(ans)>0.05 and abs(ans-sin(rad(n*th)))>0.05"),
    T("m12_regress", "Correlation and Regression", ["regression", "coefficient", "correlation", "deviation"], ["r=[0.6,0.8,0.5,0.9]", "sy=[4,6,8]", "sx=[2,3,4]"],
      r"The correlation coefficient is $r = @r@$, $\sigma_y = @sy@$ and $\sigma_x = @sx@$. Find the regression coefficient $b_{yx}$.", "r*sy/sx", ["r*sx/sy", "r*sy*sx", "sy/sx", "r/(sy*sx)"],
      r"$b_{yx} = r\dfrac{\sigma_y}{\sigma_x}$.", "the regression coefficient", [r"$b_{yx} = @r@\times\dfrac{@sy@}{@sx@}$", r"$b_{yx} = @ans@$"]),
    T("m12_binom_prob", "Probability", ["binomial", "distribution", "trials", "successes"], ["n=[4,5,6]", "r=[2,3]", "p=[0.5,0.2,0.4]"],
      r"A coin-like trial succeeds with probability $@p@$. In $@n@$ independent trials, find the probability of exactly $@r@$ successes.", "comb(n,r)*p**r*(1-p)**(n-r)",
      ["p**r", "comb(n,r)*p**r", "comb(n,r)*p**r*(1-p)**r", "comb(n,r)*(1-p)**r*p**(n-r)"], r"$P(X=r) = {}^nC_r\,p^rq^{n-r}$.", "the binomial distribution",
      [r"$P = {}^{@n@}C_{@r@}(@p@)^{@r@}(1-@p@)^{@n@-@r@}$", r"$P = @ans@$"], cond="ans>0 and abs(ans-comb(n,r)*(1-p)**r*p**(n-r))>0.002"),
    T("m12_exp_growth", "Differential Equations", ["differential", "equation", "growth", "exponential", "solution"], ["y0=[100,200,500]", "k=[0.1,0.2,0.05]", "t=[2,5,10]"],
      r"The quantity $y$ satisfies $\dfrac{dy}{dt} = @k@y$ with $y(0) = @y0@$. Find $y(@t@)$.", "y0*exp(k*t)", ["y0*k*t", "y0*exp(k+t)", "y0+k*t", "y0*exp(k)*t"], r"Solving $\dfrac{dy}{y} = k\,dt$ gives $y = y_0e^{kt}$.", "the solution of $y' = ky$",
      [r"$y = @y0@\,e^{@k@\times@t@}$", r"$y(@t@) = @ans@$"]),
]
DROP = {"math12": ["pythag", "pct_change", "circle_area", "sphere_vol", "arc", "comp_int"], "math11": ["pythag", "pct_change", "trap_area"]}  # class 9/10 topics (finance, land area)


def apply(path):
    D = json.load(open(path, encoding="utf-8")); mine = {t["id"]: t for t in M11 + M12}; have = {t["id"] for t in D["templates"]}
    D["templates"] = [mine.get(t["id"], t) for t in D["templates"]] + [t for t in mine.values() if t["id"] not in have]
    json.dump(D, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); return len(mine) - len(have & set(mine))


if __name__ == "__main__":
    for p in ("engine/param_templates.json", "docs/model/templates.json"): print(p, "added", apply(os.path.join(R, p)))
    sp = os.path.join(R, "packs", "pack_specs.json"); cur = json.load(open(sp))
    for pid, ts in (("math11", M11), ("math12", M12)):
        cur[pid]["numeric"] = [x for x in cur[pid].setdefault("numeric", []) if x not in DROP[pid]]
        for t in ts:
            if t["id"] not in cur[pid]["numeric"]: cur[pid]["numeric"].append(t["id"])
        print(pid, len(cur[pid]["numeric"]))
    json.dump(cur, open(sp, "w"), indent=1)
