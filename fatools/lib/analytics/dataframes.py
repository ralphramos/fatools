
from pandas import DataFrame, pivot_table



class AlleleDataFrame(object):

    def __init__(self, dbh, sample_ids, marker_ids, params):
        self.sample_ids = sample_ids
        self.marker_ids = marker_ids
        self.params = params
        self._df = dbh.get_allele_dataframe(self.sample_ids, self.marker_ids,
                        self.params)
        self._dominant_df = None

        # grouped dataframe based on [ 'marker_id', 'value']
        self._group_df = None
        self._group_dominant_df = None

        # distributions
        self._df_distribution = None
        self._dominant_df_distribution = None


    @property
    def df(self):
        return self._df


    @property
    def dominant_df(self):
        """ return Pandas dataframe of (marker_id, sample_id, bin, size, height) """
        if self._dominant_df is None:
            df = self.df
            idx = df.groupby(['marker_id','sample_id'])['height'].transform(max) == df['height']
            self._dominant_df = df[idx]
        return self._dominant_df


    @property
    def grouped_df(self):
        """ return Pandas dataframe grouped by ['marker_id', 'value'] """
        if self._group_df is None:
            self._group_df = self.df.groupby( ['marker_id', 'value'] )
        return self._group_df


    @property
    def grouped_dominant_df(self):
        """ return Pandas dataframe for dominant alleles group by ['marker_id', 'value'] """
        if self._group_dominant_df is None:
            self._group_dominant_df = self.dominant_df.groupby(['marker_id', 'value'])
        return self._group_dominant_df


    @property
    def df_distribution(self):
        if self._df_distribution is None:
            self._df_distribution = pivot_table(self.df,
                    rows = ['marker_id', 'value'],
                    values = 'sample_id',
                    aggfunc = len)
        return self._df_distribution


    @property
    def dominant_df_distribution(self):
        if self._df_distribution is None:
            self._dominant_df_distribution = pivot_table(self.dominant_df,
                    rows = ['marker_id', 'value'],
                    values = 'sample_id',
                    aggfunc = len)
        return self._dominant_df_distribution
