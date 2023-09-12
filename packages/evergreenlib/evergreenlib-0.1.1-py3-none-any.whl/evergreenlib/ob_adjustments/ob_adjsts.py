from evergreenlib import ExcelParser_retain_duplicates, MasterData
import numpy as np
import pandas as pd

pd.options.display.width = None
pd.options.mode.use_inf_as_na = True

class OBAdj:
    """
    This class shall be  used for getting OB adjustments from accounting files
    """

    def __init__(self, filepath, sht_name):
        self.dataframe = ExcelParser_retain_duplicates(filepath, sht_name, "Rus Account").read_data()
        self.dataframe = self.dataframe.iloc[:,slice(1,13)]
        self.dataframe['Corp Acc'] = self.dataframe['Corp Acc']. \
            astype(str).str.split(".").str.get(0)
        self.master_data = MasterData().further_process()
        self.master_data['Corp Acc'] = self.master_data['Corp Acc'].\
            astype(str).str.split(".").str.get(0)
        self.dataframe = self.dataframe[self.dataframe['Corp Acc'].isin(self.master_data['Corp Acc'])]

        self.mydict = self.master_data.drop_duplicates(subset='Rus Account', keep='first').set_index("Rus Account").T.to_dict()
        self.mydict2 = self.master_data.set_index('Corp Acc').T.to_dict()

    def further_process(self):
        self.dataframe.columns = ['col' + str(x) for x in range(len(self.dataframe.columns))]
        cols_to_be = [
            'Rus Account', 'Corp Acc', 'RUS_Text', 'ENG_Text', 'Initials_Dr', 'Initials_Cr',
            'OB_adj_Dr', 'OB_adj_Cr', 'Accruals_Dr', 'Accruals_Cr', 'CB_Dr', 'CB_Cr', 'Acc_Group']
        self.dataframe = self.dataframe.rename(columns=dict(zip(self.dataframe.columns, cols_to_be)))
        merged_df = pd.merge(self.dataframe, self.master_data, on='Corp Acc', how='left',
                             sort=False)
        return merged_df

    def reveal_ob_adjustments(self):
        df = self.further_process().copy()
        print(df.columns)

        @np.vectorize
        def check_if_none(x, y):
            if x in [0, None, ""] and y in [0, None, ""]:
                return False
            else:
                return True

        df = df[check_if_none(df['OB_adj_Dr'], df['OB_adj_Cr'])]

        df.rename(columns={'Corp Acc': 'Corp Account',
                           'ENG_Text': 'Corp Account Name',
                           'Rus Account_y': 'Rap Account'
                           }, inplace=True)

        @np.vectorize
        def func1(x, y):
            if x in [None, "None", '0.0',0] and y not in [None, "None", '0.0',0]:
                return y
            elif x not in [None, "None", '0.0',0] and y in [None, "None", '0.0',0]:
                return x

        df['Amount in LC'] = func1(df['OB_adj_Dr'], df['OB_adj_Cr'])
        cols_to_select = ['Corp Account', 'Corp Account Name', 'Rap Account', 'Amount in LC', 'Category','reporting_line']
        df = df[cols_to_select]
        df['Transaction Type'] = 'Opening Balance adjustment'
        df['Pstng Date'] = pd.to_datetime('01/01/2023').date()
        df['Param'] = 'Before due date'
        df['Text'] = 'This is opening balance adjustment at the beginning of the 2023 year'
        df['Amount in LC'] = df['Amount in LC'].astype(str).str.split(".").str.get(0).astype(float)

        df.loc[:, "Group Account Number"] = df.loc[:, "Corp Account"] \
            .apply(lambda x: self.mydict2.get(x).get("Consolidation Account") if self.mydict2.get(x) else x)
        df.loc[:, "Group Account Name"] = df.loc[:, "Corp Account"] \
            .apply(lambda x: self.mydict2.get(x).get("Consolidation Account Name") if self.mydict2.get(x) else x)
        df.loc[:, "Group Account Name_Korean"] = df.loc[ :, "Corp Account" ].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account Korean Name") if self.mydict2.get(x) else x)

        return df

    def reveal_ob_adj_ARAP(self):
        df = self.reveal_ob_adjustments().copy()
        df = df[df['reporting_line'].isin(['AR','AP','Other AR', 'Other AP'])]
        df['Category'] = df['reporting_line']
        df['Amount in LC'] = df['Amount in LC'].astype(str).str.split(".").str.get(0).astype(float)

        conds = [
            df['reporting_line'].isin(["AP", "Other AP"])
        ]

        choices = [
            df['Amount in LC'] * -1
        ]

        df['Amount in LC'] = np.select(conds, choices, default=df['Amount in LC'])


        return df



if __name__ == '__main__':
    x = OBAdj(r'V:\Accounting\Work\Мерц\2023\3 квартал\Июль 2023\Отчетность\Detail_July_2023.xlsx',
              'ОСВ_Июль_2023')
    print(x.reveal_ob_adj_ARAP().to_clipboard())
