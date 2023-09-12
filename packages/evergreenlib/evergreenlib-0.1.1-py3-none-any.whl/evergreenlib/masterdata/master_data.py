from evergreenlib import ExcelParser
import pandas as pd
import numpy as np 



class MasterData:
    """"""
    def __init__(self):
        self.tb = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS TB structure_2023.xlsx',
                              'TB_01_07_2023', 'Local Account Code').read_data()
        self.pl = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS PL structure_2023.xlsx',
                              'Sheet1', 'Local Account Code').read_data()
        self.bs = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS BS structure_2023.xlsx',
                              'Sheet1', 'Local Account Code').read_data()
        self.osv = ExcelParser(r"V:\Findep\Incoming\test\DevOps\References\HMCIS OSV structure_2023.xlsx",
                               'Sheet1',
                               'Rus Account').read_data()
        self.korean_reference = ExcelParser(
            r"V:\Findep\Incoming\test\DevOps\HSE1_CoA\Current CoA_2023.xlsx",
            'Sheet1',
            'col1').read_data()
        self.korean_reference[self.korean_reference.columns[8]] = \
            self.korean_reference[self.korean_reference.columns[8]].astype(str).str.split(".").str.get(0)

    def clean_osv(self):
        self.osv['Rus Account'] = self.dates_to_strings(self.osv['Rus Account'].astype(str))
        self.osv['Corp Acc'] = self.osv['Corp Acc'].astype(str).str.split('.').str.get(0)
        self.osv = self.osv.loc[:, ['Rus Account', 'Corp Acc', 'Text']]
        return self.osv

    def clean_bs(self):
        self.bs['Consolidation Account Code'] = self.bs['Consolidation Account Code']. \
            astype(str).str.split(".").str.get(0)
        conds_bs = [(self.bs['Consolidation Account Code'].str.len() == 5) |
                    (self.bs['Consolidation Account Code'].str.len() == 3)]

        choices_bs = [self.bs['Consolidation Account Code']]

        self.bs['FS Line'] = np.select(conds_bs, choices_bs, default=None)
        self.bs['FS Line'] = self.bs['FS Line'].ffill()
        self.bs.drop_duplicates(subset=['Consolidation Account Code'], keep='first', inplace=True)
        mydict = self.bs[['Consolidation Account Code', 'Account Name']].set_index(
            'Consolidation Account Code'
        ).T.to_dict()
        self.bs['FS Line Name'] = self.bs['FS Line'].apply(
            lambda x: mydict.get(x).get('Account Name') if mydict.get(x) is not None else x)
        self.bs = self.bs.loc[:, ['Account Tree',
                                  'Local Account Code', 'Local Account Name',
                                  'FS Line', 'FS Line Name']]
        self.bs = self.bs[pd.notna(self.bs.loc[:, 'Local Account Code'])]
        self.bs['Local Account Code'] = self.bs['Local Account Code'].astype(str).str.split('.').str.get(0)
        return self.bs

    def clean_tb(self):
        self.tb['Local Account Code'] = self.tb['Local Account Code'].astype(str).str.split('.').str.get(0)
        self.tb = self.tb[['Local Account Code', 'Local Account Name', 'Consolidation Account',
                           'Consolidation Account Name']]
        return self.tb

    def clean_pl(self):
        self.pl['Consolidation Account Code'] = (self.pl['Consolidation Account Code'].astype(str).
                                                 str.split('.').str.get(0))

        conds = [(self.pl['Consolidation Account Code'].str.len() == 5) |
                 (self.pl['Consolidation Account Code'].str.len() == 3)]

        choices = [self.pl['Consolidation Account Code']]

        self.pl['FS Line'] = np.select(conds, choices, default=None)

        self.pl['FS Line'] = self.pl['FS Line'].ffill()
        self.pl.drop_duplicates(subset=['Consolidation Account Code'], keep='first', inplace=True)

        mydict = (self.pl[['Consolidation Account Code', 'Account Name']].
                  set_index('Consolidation Account Code').T.to_dict())
        self.pl['FS Line Name'] = self.pl['FS Line'].apply(
            lambda x: mydict.get(x).get('Account Name')
            if mydict.get(x) is not None else x)
        self.pl = self.pl.loc[:, ['Local Account Code', 'Local Account Name', 'FS Line', 'FS Line Name']]
        self.pl = self.pl[pd.notna(self.pl.loc[:, 'Local Account Code'])]
        self.pl['Local Account Code'] = self.pl['Local Account Code'].astype(str).str.split('.').str.get(0)

        return self.pl

    def further_process(self):

        concatenated_df = pd.concat([self.clean_bs(), self.clean_pl()], ignore_index=False)
        concatenated_df.sort_values(by='Local Account Code', ascending=True, inplace=True)

        combined_1 = pd.merge(self.clean_osv(), self.clean_tb(), left_on='Corp Acc',
                              right_on='Local Account Code', sort=False, how='left')

        combined_1['FS Line'] = combined_1['Consolidation Account'].astype(str).str[:5]

        mydict2 = (concatenated_df[['FS Line', 'FS Line Name']].drop_duplicates().
                   set_index("FS Line").T.to_dict())

        combined_1['FS Line Name'] = combined_1['FS Line'].apply(
            lambda x: mydict2.get(x).get('FS Line Name') if mydict2.get(x) is not None else x)

        conds = [
            combined_1['Corp Acc'].isin(['11100101']),
            combined_1['Corp Acc'].isin(['11100100']),
            combined_1['Corp Acc'].isin(['11100097']),
            combined_1['Corp Acc'].isin(['A21009013']),
            combined_1['Corp Acc'].isin(['61000302']),
            combined_1['Corp Acc'].isin(['62000206', 'A62000206', 'A61000306']),
        ]

        choices_1 = ['11130040', '11102191', '11130040', '21116390', '62002010', '61002010']
        choices_2 = ['Ordinary Account (Local Currency)', 'Cash Equivalents_Other Deposits_Others_Local Currency',
                     'Ordinary Account (Local Currency)', 'Other AP_Taxes and Dues_Others',
                     'Loss on Foreign Currency Translations_Operating',
                     'Loss on Foreign Currency Translations_Operating',
                     ]
        choices_3 = ['11130', '11102', '11130', '21116',
                     '62002',
                     '62002']
        choices_4 = ['Ordinary Account (Local Currency)', 'Cash Equivalents',
                     'Ordinary Account (Local Currency)', 'Other AP_Taxes and Dues',
                     'Loss on Foreign Currency Translations',
                     'Loss on Foreign Currency Translations'
                     ]

        combined_1['Consolidation Account'] = np.select(conds, choices_1, default=combined_1['Consolidation Account'])
        combined_1['Consolidation Account Name'] = np.select(conds, choices_2,
                                                             default=combined_1['Consolidation Account Name'])
        combined_1['FS Line'] = np.select(conds, choices_3, default=combined_1['FS Line'])
        combined_1['FS Line Name'] = np.select(conds, choices_4, default=combined_1['FS Line Name'])
        combined_1['Category'] = combined_1['Consolidation Account'].apply(lambda x: str(x)[:4])
        combined_1['reporting_line'] = pd.cut(combined_1['Category'],
                                              ['1110', '1120', '1139', '1150', '1160', '1180', '1200',
                                               '1220', '1250', '1260', '1270', '1400', '2109', '2111',
                                               '2112', '2113', '2140', '2160', '2180', '2260', '2270',
                                               '2290', '3100', '3500', '4100', '4108', '4200', '4202', '4300',
                                               '5100', '5200', '6100', '6200', '7100', '7200',
                                               '7400', '7900', '8000'],
                                              labels=['Cash and Cash Equivalents',
                                                      'Other Assets, Current',
                                                      'AR',
                                                      "Other AR",
                                                      'Inventories',
                                                      'Short-Term Investments',
                                                      None,
                                                      'Long-Term Loans and Receivables',
                                                      'PPE',
                                                      None,
                                                      'Intangible Assets',
                                                      'Right-of-use Asset',
                                                      "AP",
                                                      "Other AP",
                                                      "Other AP",
                                                      None,
                                                      'Other Liabilities, Current',
                                                      '(Current)Provision',
                                                      '(Current)Lease Liabilities',
                                                      'Provision, Non-Current',
                                                      'Deferred Tax Liabilities',
                                                      'Lease Liabilities, Non-Current',
                                                      'Capital stock',
                                                      'Retained earnings',
                                                      'Sales Revenue',
                                                      'Sales Adjustment_incentive',
                                                      'COGS',
                                                      'Other COGS',
                                                      None,
                                                      'SG&A expenses',
                                                      None,
                                                      'Other operating income',
                                                      'Other operating expenses',
                                                      'Financial income',
                                                      'Financial expenses',
                                                      'Net Income_NCI',
                                                      'Income tax expenses',

                                                      ],
                                              right=False,
                                              ordered=False)

        conds = [
            (combined_1['reporting_line'] == 'PPE') & (combined_1['Consolidation Account Name'].str.contains("Dep")),
            (combined_1['reporting_line'] == 'Right-of-use Asset') & (
                combined_1['Consolidation Account Name'].str.contains("Dep"))
        ]
        choices = [
            'PPE_Accumulated Depreciation',
            'Right-of-use Asset_Accumulated Depreciation'
        ]
        combined_1['reporting_line'] = np.select(conds, choices, default=combined_1['reporting_line'])

        conds_2 = [
            (combined_1['Rus Account'].astype(str).str.startswith("55")) & (pd.isna(combined_1['reporting_line'])),
            (combined_1['Rus Account'].astype(str).str.startswith("68.02")) & (pd.isna(combined_1['reporting_line'])),
            (combined_1['Rus Account'].astype(str).str.startswith("76.13.01")) & (pd.isna(combined_1['reporting_line'])),
            (combined_1['Rus Account'].astype(str).str.startswith("76.14.01")) & (pd.isna(combined_1['reporting_line']))
        ]

        choices_6 = [
            '1110',
            '2142',
            '1151',
            '2112',
        ]

        choices_7 = [
            'Cash and Cash Equivalents',
            'Other Liabilities, Current',
            'Other AR',
            'Other AP'
        ]

        choices_8 = [
            '11102',
            '21421',
            '11518',
            '21129'
        ]

        choices_9 = [
            'Cash Equivalents',
            'VAT Payables',
            'Other AR_Others',
            'Other AP_Others'
        ]
        

        combined_1['Category'] = np.select(conds_2, choices_6, default=combined_1['Category'])
        combined_1['reporting_line'] = np.select(conds_2, choices_7, default=combined_1['reporting_line'])
        combined_1['FS Line'] = np.select(conds_2, choices_8, default=combined_1['FS Line'])
        combined_1['FS Line Name'] = np.select(conds_2, choices_9, default=combined_1['FS Line Name'])

        combined_1['Consolidation Account'] = np.where(combined_1['Corp Acc']=='11011207','11518041',combined_1['Consolidation Account'])
        combined_1['Consolidation Account'] = np.where(combined_1['Corp Acc']=='21000211','21129990',combined_1['Consolidation Account'])

        combined_1['Consolidation Account Name'] = np.where(combined_1['Corp Acc']=='11011207','Other AR_Others_Foreign Currency',
                                                            combined_1['Consolidation Account Name'])
        combined_1['Consolidation Account Name'] = np.where(combined_1['Corp Acc']=='21000211','Other AP_Others',
                                                            combined_1['Consolidation Account Name'])




        special_cond = [
            combined_1['Category'].str.startswith(('1', '2', '3')),
            combined_1['Category'].str.startswith(('4', '5', '6', '7')),
        ]
        choices_5 = [
            'bs',
            'pl',
        ]
        combined_1['accounting group'] = np.select(special_cond, choices_5, default='')
        combined_1['Consolidation Account'] = (
            combined_1['Consolidation Account'].astype(str).str.split(".").str.get(0))

        korean_ref = self.korean_reference.set_index(self.korean_reference.columns[8]).T.to_dict()

        combined_1['Consolidation Account Korean Name'] = \
            combined_1['Consolidation Account'].apply(lambda x: korean_ref.get(x).get('계정명')
            if korean_ref.get(x) else None)

        return combined_1

    @staticmethod
    @np.vectorize
    def dates_to_strings(col: pd.Series):
        if len(col) == 8:
            return col
        elif col in [None, "None"]:
            return None
        elif len(col) == 5 or len(col) == 7 or len(col) == 9:
            return col
        else:
            try:
                return pd.to_datetime(col, dayfirst=False).strftime('%d.%m.%y')
            except ValueError:
                pass


if __name__ == '__main__':
    x = MasterData()
    # print(x.further_process().to_clipboard())
    x.further_process().to_clipboard()
