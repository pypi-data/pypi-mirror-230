from __future__ import annotations

import numpy as np

from snapatac2._snapatac2 import AnnData, AnnDataSet
from snapatac2.tools._misc import aggregate_X
from snapatac2._utils import find_elbow
from ._base import render_plot, heatmap, kde2d, scatter, scatter3d
from ._network import network_scores, network_edge_stat

__all__ = [
    'tsse', 'scrublet', 'umap', 'network_scores', 'spectral_eigenvalues',
    'regions', 'motif_enrichment',
]

def tsse(
    adata: AnnData,
    min_fragment: int = 500,
    width: int = 500,
    height: int = 400,
    **kwargs,
) -> 'plotly.graph_objects.Figure' | None:
    """Plot the TSS enrichment vs. number of fragments density figure.

    Parameters
    ----------
    adata
        Annotated data matrix.
    min_fragment
        The cells' unique fragments lower than it should be removed
    width
        The width of the plot
    height
        The height of the plot
    kwargs        
        Additional arguments passed to :func:`~snapatac2.pl.render_plot` to
        control the final plot output. Please see :func:`~snapatac2.pl.render_plot`
        for details.

    Returns
    -------
    'plotly.graph_objects.Figure' | None
        If `show=False` and `out_file=None`, an `plotly.graph_objects.Figure` will be 
        returned, which can then be further customized using the plotly API.

    Examples
    --------
    .. plotly::

        >>> import snapatac2 as snap
        >>> data = snap.read(str(snap.datasets.pbmc5k(type='gene')))
        >>> fig = snap.pl.tsse(data, show=False, out_file=None)
        >>> fig.show()
    """
    selected_cells = np.where(adata.obs["n_fragment"] >= min_fragment)[0]
    x = adata.obs["n_fragment"][selected_cells]
    y = adata.obs["tsse"][selected_cells]

    fig = kde2d(x, y, log_x=True, log_y=False)
    fig.update_layout(
        xaxis_title="Number of unique fragments",
        yaxis_title="TSS enrichment score",
    )

    return render_plot(fig, width, height, **kwargs)

'''
def scrublet(
    adata: AnnData,
    width: int = 800,
    height: int = 400,
    show: bool = True,
    interactive: bool = True,
    out_file: str | None = None,
) -> 'plotly.graph_objects.Figure' | None:
    """Plot the doublet score distribution.

    Parameters
    ----------
    adata
        Annotated data matrix.
    width
        The width of the plot
    height
        The height of the plot
    show
        Show the figure.
    interactive
        Whether to make interactive plot
    out_file
        Path of the output file for saving the output image, end with
        '.svg' or '.pdf' or '.png' or '.html'.

    Returns
    -------
    'plotly.graph_objects.Figure' | None
        If `show=False` and `out_file=None`, an `plotly.graph_objects.Figure` will be 
        returned, which can then be further customized using the plotly API.
    """
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    doublet_scores = adata.obs["doublet_score"].to_numpy()
    sim_scores = adata.uns["scrublet_sim_doublet_score"]

    thres = adata.uns["scrublet_threshold"] if "scrublet_threshold" in adata.uns else None

    if thres is None:
        title1 = "Observed cells"
        title2 = "Simulated doublets"
    else:
        p1 = (doublet_scores >= thres).sum() / doublet_scores.size
        p2 = (sim_scores >= thres).sum() / sim_scores.size
        title1 = "Observed cells ({:.2%} doublets)".format(p1)
        title2 = "Simulated doublets ({:.2%} doublets)".format(p2)

    fig = make_subplots(rows=1, cols=2, subplot_titles=[title1, title2])

    fig.add_trace(go.Histogram(x=doublet_scores),row=1, col=1)
    if thres is not None:
        fig.add_vline(x=thres, line_width=3, line_dash="dash", line_color="green")
        fig.add_vrect(x0=thres, x1 = doublet_scores.max(), line_width=0, fillcolor="red", opacity=0.2)

    fig.add_trace(go.Histogram(x=sim_scores), row=1, col=2)
    if thres is not None:
        fig.add_vline(x=thres, line_width=3, line_dash="dash", line_color="green")
        fig.add_vrect(x0=thres, x1 = sim_scores.max(), line_width=0, fillcolor="red", opacity=0.2)

    fig.update(layout_showlegend=False)
    return render_plot(fig, width, height, interactive, show, out_file)
'''

def spectral_eigenvalues(
    adata: AnnData,
    width: int = 600,
    height: int = 400,
    show: bool = True,
    interactive: bool = True,
    out_file: str | None = None,
) -> 'plotly.graph_objects.Figure' | None:
    """Plot the eigenvalues of spectral embedding.

    Parameters
    ----------
    adata
        Annotated data matrix.
    width
        The width of the plot
    height
        The height of the plot
    show
        Show the figure.
    interactive
        Whether to make interactive plot
    out_file
        Path of the output file for saving the output image, end with
        '.svg' or '.pdf' or '.png' or '.html'.

    Returns
    -------
    'plotly.graph_objects.Figure' | None
        If `show=False` and `out_file=None`, an `plotly.graph_objects.Figure` will be 
        returned, which can then be further customized using the plotly API.
    """
 
    import plotly.express as px
    import pandas as pd

    data = adata.uns["spectral_eigenvalue"]

    df = pd.DataFrame({"Component": map(str, range(1, data.shape[0] + 1)), "Eigenvalue": data})
    fig = px.scatter(df, x="Component", y="Eigenvalue", template="plotly_white")
    n = find_elbow(data)
    adata.uns["num_eigen"] = n
    fig.add_vline(x=n)

    return render_plot(fig, width, height, interactive, show, out_file)

def regions(
    adata: AnnData | AnnDataSet,
    groupby: str | list[str],
    peaks: dict[str, list[str]],
    width: float = 600,
    height: float = 400,
    show: bool = True,
    interactive: bool = True,
    out_file: str | None = None,
) -> 'plotly.graph_objects.Figure' | None:
    """
    Parameters
    ----------
    adata
        Annotated data matrix.
    groupby
        Group the cells into different groups. If a `str`, groups are obtained from
        `.obs[groupby]`.
    peaks
        Peaks of each group.
    width
        The width of the plot
    height
        The height of the plot
    show
        Show the figure
    interactive
        Whether to make interactive plot
    out_file
        Path of the output file for saving the output image, end with
        '.svg' or '.pdf' or '.png' or '.html'.

    Returns
    -------
    'plotly.graph_objects.Figure' | None
        If `show=False` and `out_file=None`, an `plotly.graph_objects.Figure` will be 
        returned, which can then be further customized using the plotly API.
    """
    import polars as pl
    import plotly.graph_objects as go

    count = aggregate_X(adata, groupby=groupby, normalize="RPKM")
    names = count.obs_names
    count = pl.DataFrame(count.X.T)
    count.columns = list(names)
    idx_map = {x: i for i, x in enumerate(adata.var_names)}
    idx = [idx_map[x] for x in np.concatenate(list(peaks.values()))]
    mat = np.log2(1 + count.to_numpy()[idx, :])

    trace = go.Heatmap(
        x=count.columns,
        y=np.concatenate(list(peaks.values()))[::-1],
        z=mat,
        type='heatmap',
        colorscale='Viridis',
        colorbar={ "title": "log2(1 + RPKM)" },
    )
    data = [trace]
    layout = {
        "yaxis": { "visible": False, "autorange": "reversed" },
        "xaxis": { "title": groupby },
    }
    fig = go.Figure(data=data, layout=layout)
    return render_plot(fig, width, height, interactive, show, out_file)

def umap(
    adata: AnnData,
    color: str | np.ndarray | None = None,
    use_rep: str = "X_umap",
    marker_size: float = None,
    marker_opacity: float = 1,
    sample_size: int | None = None,
    **kwargs,
) -> 'plotly.graph_objects.Figure' | None:
    """Plot the UMAP embedding.

    Parameters
    ----------
    adata
        Annotated data matrix.
    color
        If the input is a string, it will be used the key to retrieve values from
        `obs`.
    use_rep
        Use the indicated representation in `.obsm`.
    marker_size
        Size of the dots.
    marker_opacity
        Opacity of the dots.
    sample_size
        If the number of cells is larger than `sample_size`, a random sample of
        `sample_size` cells will be used for plotting.
    kwargs        
        Additional arguments passed to :func:`~snapatac2.pl.render_plot` to
        control the final plot output. Please see :func:`~snapatac2.pl.render_plot`
        for details.

    Returns
    -------
    'plotly.graph_objects.Figure' | None
        If `show=False` and `out_file=None`, an `plotly.graph_objects.Figure` will be 
        returned, which can then be further customized using the plotly API.
    """
    from natsort import index_natsorted

    embedding = adata.obsm[use_rep] 

    if isinstance(color, str):
        groups = adata.obs[color].to_numpy()
    else:
        groups = color
        color = "color"
    
    if sample_size is not None and adata.shape[0] > sample_size:
        idx = np.random.choice(adata.shape[0], sample_size, replace=False)
        embedding = embedding[idx, :]
        if groups is not None: groups = groups[idx]

    if groups is not None:
        idx = index_natsorted(groups)
        embedding = embedding[idx, :]
        groups = [groups[i] for i in idx]

    if marker_size is None:
        num_points = embedding.shape[0]
        marker_size = (1000 / num_points)**(1/3) * 3

    if embedding.shape[1] >= 3:
        return scatter3d(embedding[:, 0], embedding[:, 1], embedding[:, 2], color=groups,
            x_label="UMAP-1", y_label="UMAP-2", z_label="UMAP-3", color_label=color,
            marker_size=marker_size, marker_opacity=marker_opacity, **kwargs)
    else:
        return scatter(embedding[:, 0], embedding[:, 1], color=groups,
            x_label="UMAP-1", y_label="UMAP-2", color_label=color,
            marker_size=marker_size, marker_opacity=marker_opacity, **kwargs)

def motif_enrichment(
    enrichment: list(str, 'pl.DataFrame'),
    min_log_fc: float = 1,
    max_fdr: float = 0.01,
    **kwargs,
) -> 'plotly.graph_objects.Figure' | None:
    """Plot the motif enrichment result.

    Parameters
    ----------
    enrichment
        Motif enrichment result.
    min_log_fc
        Retain motifs that satisfy: log2-fold-change >= `min_log_fc`.
    max_fdr
        Retain motifs that satisfy: FDR <= `max_fdr`.
    kwargs        
        Additional arguments passed to :func:`~snapatac2.pl.render_plot` to
        control the final plot output. Please see :func:`~snapatac2.pl.render_plot`
        for details.

    Returns
    -------
    'plotly.graph_objects.Figure' | None
        If `show=False` and `out_file=None`, an `plotly.graph_objects.Figure` will be 
        returned, which can then be further customized using the plotly API.
    """
 
    import pandas as pd
    
    fc = np.vstack([df['log2(fold change)'] for df in enrichment.values()])
    filter1 = np.apply_along_axis(lambda x: np.any(np.abs(x) >= min_log_fc), 0, fc)
    
    fdr = np.vstack([df['adjusted p-value'] for df in enrichment.values()])
    filter2 = np.apply_along_axis(lambda x: np.any(x <= max_fdr), 0, fdr)

    passed = np.logical_and(filter1, filter2)
    
    sign = np.sign(fc[:, passed])
    pvals = np.vstack([df['p-value'].to_numpy()[passed] for df in enrichment.values()])
    minval = np.min(pvals[np.nonzero(pvals)])
    pvals = np.clip(pvals, minval, None)
    pvals = sign * np.log(-np.log10(pvals))

    df = pd.DataFrame(
        pvals.T,
        columns=list(enrichment.keys()),
        index=next(iter(enrichment.values()))['id'].to_numpy()[passed],
    )
      
    return heatmap(
        df.to_numpy(),
        row_names=df.index,
        column_names=df.columns,
        colorscale='RdBu_r',
        **kwargs,
    )