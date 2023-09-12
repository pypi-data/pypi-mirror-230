Module uim.utils.statistics
===========================

Classes
-------

`StatisticsAnalyzer()`
:   Statistics analyzer
    ===================
    Analyze the model and compute statistics.

    ### Ancestors (in MRO)

    * uim.utils.analyser.ModelAnalyzer
    * abc.ABC

    ### Static methods

    `analyze(model: uim.model.ink.InkModel, ignore_predicates: Optional[List[str]] = None, ignore_properties: Optional[List[str]] = None)`
    :   Analyze the model and compute statistics.
        Parameters
        ----------
        model: InkModel
            Ink model to analyze.
        ignore_predicates: Optional[List[str]]
            List of predicates to ignore.
        ignore_properties: Optional[List[str]]
            List of properties to ignore.

    `merge_stats(*stats)`
    :

    `summarize(stats, verbose=False)`
    :