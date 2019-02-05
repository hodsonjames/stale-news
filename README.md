# stale-news
Repository for code related to research on the effect of old news on financial markets.

https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2433234

## Abstract

Why do investors react to old information? We posit that it is cognitively difficult to identify old content combined from multiple sources. We use a unique dataset of all news passing through the Bloomberg terminal to differentiate "recombination" stories that draw content from several sources from direct "reprints." Firms see larger price moves on days when they have more recombination stories relative to reprints. Furthermore, while overall reactions to old information have declined over time, differential reactions to recombination stories have risen. Altogether, these results point to investors' increased sophistication in discarding reprints, but continuing susceptibility to recombination of old information 

## Code

There are two parts to this code repository. Replication, and News Staleness Measures.

### Replication

The first part represents code that allows for the reproduction of the results calculated for the paper on any appropriately formatted news archive. The paper was originally written using an archive of news provided by Bloomberg LP for the period 2000-2014. This consisted of news stories aggregated from roughly 100,000 sources across the web, as well as premium, regional, and specialty news subscriptions. Additional tests have been run on a comparable corpus from Dow Jones News Corp. that spans 2000-2018. We would expect the measure to be robust to similar financial news aggregators and time spans.

### Staleness Measures

The second part provides a variety of additional measures of news staleness that may be substituted for the 'simple' modified word overlap measures from the paper.

### Additional Experiments

We maintain a module of additional experiments with the news archives, news analytics data, and other data sources that may help with robustness checks, reviewer comments, and other ML-based measures relevant to the paper.

## Thanks

We acknowledge the contribution of the following research assistants from UC Berkeley for this work...
