Maintainer backlog notebooks

Diebold Mariano tutorial
 - Rename it
 - Practical example needs a heading - looks like it's under the References heading
 - 'stats community' --> 'statistics community'

RMSE tutorial
 - Use RMSE to Focus on Anomalies and understandably
 - grammar and capitalisation

Naming of scores.stats.tests

Options:
  scores.stats.tests.diebold_mariano <-- current
  scores.stats.diebold_mariano  <-- shorter, but doesn't distinguish tests from other stats functions in the namespace
  scores.stats.statatistical_tests.diebold_mariano <-- probably the clearest, just a long name
  scores.stats.statstests.diebold_mariano <-- slightly shorter, slightly less clear
  scores.stats.stats_tests.diebold_mariano <-- slightly shorter, slightly less clear
  scores.statistical_tests.diebold_mariano <-- shorter but other statistics things can't share a namespace
  scores.stats.dm_test <-- shorter, distinguishes tests by a subtle function naming convention

  Other examples:
     https://docs.scipy.org/doc/scipy/reference/stats.html
     https://docs.python.org/3/library/statistics.html
     https://www.statsmodels.org/0.9.0/py-modindex.html

Room for improvement - CRPS docstring length and management and type hinting length

Update PyPI with version 0.4