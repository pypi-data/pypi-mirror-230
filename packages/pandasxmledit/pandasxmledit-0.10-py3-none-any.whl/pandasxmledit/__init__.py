import os.path
import re
import pandas as pd
import requests
import xmltodict
from flatten_any_dict_iterable_or_whatsoever import fla_tu, set_in_original_iter
from mymulti_key_dict import MultiKeyDict
from ast import literal_eval

def astconvert(x):
    try:
        return literal_eval(x)
    except Exception:
        return x


class PandasXMLEdit:
    r"""
    A class for editing XML data using pandas DataFrames.

    Args:
        xmldata (str, bytes, or dict): The XML data to be processed. It can be provided as a file path,
            URL, raw XML string, or a pre-parsed XML dictionary.
        convert_dtypes (bool, optional): If True, automatically attempts to convert values to their
            appropriate data types. Default is True.
        **kwargs: Additional keyword arguments to pass to xmltodict.parse() when parsing the XML data.

    Attributes:
        xmldata (bytes): The raw XML data in bytes.
        xmldict (MultiKeyDict): A multi-key dictionary representation of the XML data.
        convert_dtypes (bool): Flag to control automatic data type conversion.
        df (pandas.DataFrame): A pandas DataFrame representing the XML data.

    Methods:
        update_xml_data(**kwargs):
            Updates the original XML data with changes made to the DataFrame and returns the updated PandasXMLEdit instance.

        save_xml(filename, encoding='utf-8'):
            Saves the updated XML data to a file with the specified filename and encoding.

    Example:
        # Create a PandasXMLEdit instance with XML data from a URL
        from pandasxmledit import PandasXMLEdit
        xmledit = PandasXMLEdit(
            xmldata="https://github.com/hansalemaos/screenshots/raw/main/xmlexample.xml",
            convert_dtypes=True,
            process_namespaces=False,
        )

        # Modify values in the DataFrame
        xmledit.df.loc[xmledit.df.key_3 == 'author', 'value'] = 'Stephen King'
        xmledit.df.loc[xmledit.df.key_3 == 'price', 'value'] *= 10

        # Update the XML data with DataFrame changes
        xmledit.update_xml_data(pretty=True)

        # Display the updated XML data and its dictionary representation
        print(xmledit.xmldata)
        print(xmledit.xmldict)

        # Save the updated XML data to a file
        xmledit.save_xml(r"c:\updatedxml.xml")

    Note:
        - This class provides a convenient way to manipulate XML data using pandas DataFrames.
        - Automatic data type conversion can be enabled or disabled by setting the `convert_dtypes` attribute.
    """

    def __init__(self, xmldata, convert_dtypes=True, **kwargs):
        if isinstance(xmldata, str) and os.path.exists(xmldata):
            with open(xmldata, mode="rb") as fd:
                self.xmldata = fd.read()
        elif isinstance(xmldata, str) and re.search(
            "^https?://", xmldata[:10], flags=re.I
        ):
            try:
                with requests.get(xmldata) as r:
                    self.xmldata = r.content
            except Exception as e:
                print(e)
                self.xmldata = xmldata
        else:
            self.xmldata = xmldata
        self.xmldict = MultiKeyDict(xmltodict.parse(self.xmldata, **kwargs))
        self.convert_dtypes = convert_dtypes
        self.df = self._convert_to_df()

    def __repr__(self):
        return self.df.to_string()

    def __str__(self):
        return self.df.to_string()

    def __getattr__(self, item):
        return getattr(self.df, item)

    def __missing__(self, key):
        return self.df[key]

    def __setitem__(self, key, value):
        self.df[key] = value

    def _convert_to_df(self):
        alldi = list(fla_tu(self.xmldict))
        df = pd.concat(
            [pd.DataFrame([x[1]]).assign(value=[x[0]]).fillna(pd.NA) for x in alldi]
        ).rename(columns={"value": 999999999999})
        df = df[sorted(df.columns)].copy().rename(columns={999999999999: "value"})
        df.columns = [f"key_{x}" if isinstance(x, int) else x for x in df.columns]
        if self.convert_dtypes:
            df['value'] = df['value'].apply(astconvert)
        return df

    def update_xml_data(self, **kwargs):
        for key, item in self.df.iterrows():
            likey = []
            for col in self.df.columns[:-1]:
                v2 = item[col]
                if pd.isna(v2):
                    break
                else:
                    likey.append(v2)
            set_in_original_iter(self.xmldict, likey, str(item["value"]))
        self.xmldata = xmltodict.unparse(self.xmldict, **kwargs)
        return self

    def save_xml(self, filename, encoding='utf-8'):
        with open(filename, mode="wb") as fd:
            fd.write(self.xmldata.encode(encoding))
        return self


