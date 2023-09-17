import sys #line:47
import time #line:48
import copy #line:49
from time import strftime #line:51
from time import gmtime #line:52
import pandas as pd #line:54
import numpy #line:55
from pandas .api .types import CategoricalDtype #line:56
import progressbar #line:58
import re #line:59
class cleverminer :#line:60
    version_string ="1.0.8"#line:62
    def __init__ (O0OO0OOO0OOO00OO0 ,**OO0OO00O00OOO0O0O ):#line:64
        O0OO0OOO0OOO00OO0 ._print_disclaimer ()#line:65
        O0OO0OOO0OOO00OO0 .stats ={'total_cnt':0 ,'total_ver':0 ,'total_valid':0 ,'control_number':0 ,'start_prep_time':time .time (),'end_prep_time':time .time (),'start_proc_time':time .time (),'end_proc_time':time .time ()}#line:74
        O0OO0OOO0OOO00OO0 .options ={'max_categories':100 ,'max_rules':None ,'optimizations':True ,'automatic_data_conversions':True ,'progressbar':True ,'keep_df':False }#line:82
        O0OO0OOO0OOO00OO0 .df =None #line:83
        O0OO0OOO0OOO00OO0 .kwargs =None #line:84
        if len (OO0OO00O00OOO0O0O )>0 :#line:85
            O0OO0OOO0OOO00OO0 .kwargs =OO0OO00O00OOO0O0O #line:86
        O0OO0OOO0OOO00OO0 .verbosity ={}#line:87
        O0OO0OOO0OOO00OO0 .verbosity ['debug']=False #line:88
        O0OO0OOO0OOO00OO0 .verbosity ['print_rules']=False #line:89
        O0OO0OOO0OOO00OO0 .verbosity ['print_hashes']=True #line:90
        O0OO0OOO0OOO00OO0 .verbosity ['last_hash_time']=0 #line:91
        O0OO0OOO0OOO00OO0 .verbosity ['hint']=False #line:92
        if "opts"in OO0OO00O00OOO0O0O :#line:93
            O0OO0OOO0OOO00OO0 ._set_opts (OO0OO00O00OOO0O0O .get ("opts"))#line:94
        if "opts"in OO0OO00O00OOO0O0O :#line:95
            if "verbose"in OO0OO00O00OOO0O0O .get ('opts'):#line:96
                OO000OO00000OOOOO =OO0OO00O00OOO0O0O .get ('opts').get ('verbose')#line:97
                if OO000OO00000OOOOO .upper ()=='FULL':#line:98
                    O0OO0OOO0OOO00OO0 .verbosity ['debug']=True #line:99
                    O0OO0OOO0OOO00OO0 .verbosity ['print_rules']=True #line:100
                    O0OO0OOO0OOO00OO0 .verbosity ['print_hashes']=False #line:101
                    O0OO0OOO0OOO00OO0 .verbosity ['hint']=True #line:102
                    O0OO0OOO0OOO00OO0 .options ['progressbar']=False #line:103
                elif OO000OO00000OOOOO .upper ()=='RULES':#line:104
                    O0OO0OOO0OOO00OO0 .verbosity ['debug']=False #line:105
                    O0OO0OOO0OOO00OO0 .verbosity ['print_rules']=True #line:106
                    O0OO0OOO0OOO00OO0 .verbosity ['print_hashes']=True #line:107
                    O0OO0OOO0OOO00OO0 .verbosity ['hint']=True #line:108
                    O0OO0OOO0OOO00OO0 .options ['progressbar']=False #line:109
                elif OO000OO00000OOOOO .upper ()=='HINT':#line:110
                    O0OO0OOO0OOO00OO0 .verbosity ['debug']=False #line:111
                    O0OO0OOO0OOO00OO0 .verbosity ['print_rules']=False #line:112
                    O0OO0OOO0OOO00OO0 .verbosity ['print_hashes']=True #line:113
                    O0OO0OOO0OOO00OO0 .verbosity ['last_hash_time']=0 #line:114
                    O0OO0OOO0OOO00OO0 .verbosity ['hint']=True #line:115
                    O0OO0OOO0OOO00OO0 .options ['progressbar']=False #line:116
                elif OO000OO00000OOOOO .upper ()=='DEBUG':#line:117
                    O0OO0OOO0OOO00OO0 .verbosity ['debug']=True #line:118
                    O0OO0OOO0OOO00OO0 .verbosity ['print_rules']=True #line:119
                    O0OO0OOO0OOO00OO0 .verbosity ['print_hashes']=True #line:120
                    O0OO0OOO0OOO00OO0 .verbosity ['last_hash_time']=0 #line:121
                    O0OO0OOO0OOO00OO0 .verbosity ['hint']=True #line:122
                    O0OO0OOO0OOO00OO0 .options ['progressbar']=False #line:123
        O0OO0OOO0OOO00OO0 ._is_py310 =sys .version_info [0 ]>=4 or (sys .version_info [0 ]>=3 and sys .version_info [1 ]>=10 )#line:124
        if not (O0OO0OOO0OOO00OO0 ._is_py310 ):#line:125
            print ("Warning: Python 3.10+ NOT detected. You should upgrade to Python 3.10 or greater to get better performance")#line:126
        else :#line:127
            if (O0OO0OOO0OOO00OO0 .verbosity ['debug']):#line:128
                print ("Python 3.10+ detected.")#line:129
        O0OO0OOO0OOO00OO0 ._initialized =False #line:130
        O0OO0OOO0OOO00OO0 ._init_data ()#line:131
        O0OO0OOO0OOO00OO0 ._init_task ()#line:132
        if len (OO0OO00O00OOO0O0O )>0 :#line:133
            if "df"in OO0OO00O00OOO0O0O :#line:134
                O0OO0OOO0OOO00OO0 ._prep_data (OO0OO00O00OOO0O0O .get ("df"))#line:135
            else :#line:136
                print ("Missing dataframe. Cannot initialize.")#line:137
                O0OO0OOO0OOO00OO0 ._initialized =False #line:138
                return #line:139
            OOO0O00OOOOO0O0OO =OO0OO00O00OOO0O0O .get ("proc",None )#line:140
            if not (OOO0O00OOOOO0O0OO ==None ):#line:141
                O0OO0OOO0OOO00OO0 ._calculate (**OO0OO00O00OOO0O0O )#line:142
            else :#line:144
                if O0OO0OOO0OOO00OO0 .verbosity ['debug']:#line:145
                    print ("INFO: just initialized")#line:146
                O000O00OO0O0OO00O ={}#line:147
                O00O000O0000O0OOO ={}#line:148
                O00O000O0000O0OOO ["varname"]=O0OO0OOO0OOO00OO0 .data ["varname"]#line:149
                O00O000O0000O0OOO ["catnames"]=O0OO0OOO0OOO00OO0 .data ["catnames"]#line:150
                O000O00OO0O0OO00O ["datalabels"]=O00O000O0000O0OOO #line:151
                O0OO0OOO0OOO00OO0 .result =O000O00OO0O0OO00O #line:152
        O0OO0OOO0OOO00OO0 ._initialized =True #line:154
    def _set_opts (O00000000O0OOO0O0 ,OO0O0000OO0OO0OO0 ):#line:156
        if "no_optimizations"in OO0O0000OO0OO0OO0 :#line:157
            O00000000O0OOO0O0 .options ['optimizations']=not (OO0O0000OO0OO0OO0 ['no_optimizations'])#line:158
            print ("No optimization will be made.")#line:159
        if "disable_progressbar"in OO0O0000OO0OO0OO0 :#line:160
            O00000000O0OOO0O0 .options ['progressbar']=False #line:161
            print ("Progressbar will not be shown.")#line:162
        if "max_rules"in OO0O0000OO0OO0OO0 :#line:163
            O00000000O0OOO0O0 .options ['max_rules']=OO0O0000OO0OO0OO0 ['max_rules']#line:164
        if "max_categories"in OO0O0000OO0OO0OO0 :#line:165
            O00000000O0OOO0O0 .options ['max_categories']=OO0O0000OO0OO0OO0 ['max_categories']#line:166
            if O00000000O0OOO0O0 .verbosity ['debug']==True :#line:167
                print (f"Maximum number of categories set to {O00000000O0OOO0O0.options['max_categories']}")#line:168
        if "no_automatic_data_conversions"in OO0O0000OO0OO0OO0 :#line:169
            O00000000O0OOO0O0 .options ['automatic_data_conversions']=not (OO0O0000OO0OO0OO0 ['no_automatic_data_conversions'])#line:170
            print ("No automatic data conversions will be made.")#line:171
        if "keep_df"in OO0O0000OO0OO0OO0 :#line:172
            O00000000O0OOO0O0 .options ['keep_df']=OO0O0000OO0OO0OO0 ['keep_df']#line:173
    def _init_data (OOO00OO00OOOO0000 ):#line:176
        OOO00OO00OOOO0000 .data ={}#line:178
        OOO00OO00OOOO0000 .data ["varname"]=[]#line:179
        OOO00OO00OOOO0000 .data ["catnames"]=[]#line:180
        OOO00OO00OOOO0000 .data ["vtypes"]=[]#line:181
        OOO00OO00OOOO0000 .data ["dm"]=[]#line:182
        OOO00OO00OOOO0000 .data ["rows_count"]=int (0 )#line:183
        OOO00OO00OOOO0000 .data ["data_prepared"]=0 #line:184
    def _init_task (O0O0OO00O0O00O00O ):#line:186
        if "opts"in O0O0OO00O0O00O00O .kwargs :#line:188
            O0O0OO00O0O00O00O ._set_opts (O0O0OO00O0O00O00O .kwargs .get ("opts"))#line:189
        O0O0OO00O0O00O00O .cedent ={'cedent_type':'none','defi':{},'num_cedent':0 ,'trace_cedent':[],'trace_cedent_asindata':[],'traces':[],'generated_string':'','rule':{},'filter_value':int (0 )}#line:199
        O0O0OO00O0O00O00O .task_actinfo ={'proc':'','cedents_to_do':[],'cedents':[]}#line:203
        O0O0OO00O0O00O00O .rulelist =[]#line:204
        O0O0OO00O0O00O00O .stats ['total_cnt']=0 #line:206
        O0O0OO00O0O00O00O .stats ['total_valid']=0 #line:207
        O0O0OO00O0O00O00O .stats ['control_number']=0 #line:208
        O0O0OO00O0O00O00O .result ={}#line:209
        O0O0OO00O0O00O00O ._opt_base =None #line:210
        O0O0OO00O0O00O00O ._opt_relbase =None #line:211
        O0O0OO00O0O00O00O ._opt_base1 =None #line:212
        O0O0OO00O0O00O00O ._opt_relbase1 =None #line:213
        O0O0OO00O0O00O00O ._opt_base2 =None #line:214
        O0O0OO00O0O00O00O ._opt_relbase2 =None #line:215
        O0O00OO0OO00000O0 =None #line:216
        if not (O0O0OO00O0O00O00O .kwargs ==None ):#line:217
            O0O00OO0OO00000O0 =O0O0OO00O0O00O00O .kwargs .get ("quantifiers",None )#line:218
            if not (O0O00OO0OO00000O0 ==None ):#line:219
                for OOOO0O0OOOO0OO0OO in O0O00OO0OO00000O0 .keys ():#line:220
                    if OOOO0O0OOOO0OO0OO .upper ()=='BASE':#line:221
                        O0O0OO00O0O00O00O ._opt_base =O0O00OO0OO00000O0 .get (OOOO0O0OOOO0OO0OO )#line:222
                    if OOOO0O0OOOO0OO0OO .upper ()=='RELBASE':#line:223
                        O0O0OO00O0O00O00O ._opt_relbase =O0O00OO0OO00000O0 .get (OOOO0O0OOOO0OO0OO )#line:224
                    if (OOOO0O0OOOO0OO0OO .upper ()=='FRSTBASE')|(OOOO0O0OOOO0OO0OO .upper ()=='BASE1'):#line:225
                        O0O0OO00O0O00O00O ._opt_base1 =O0O00OO0OO00000O0 .get (OOOO0O0OOOO0OO0OO )#line:226
                    if (OOOO0O0OOOO0OO0OO .upper ()=='SCNDBASE')|(OOOO0O0OOOO0OO0OO .upper ()=='BASE2'):#line:227
                        O0O0OO00O0O00O00O ._opt_base2 =O0O00OO0OO00000O0 .get (OOOO0O0OOOO0OO0OO )#line:228
                    if (OOOO0O0OOOO0OO0OO .upper ()=='FRSTRELBASE')|(OOOO0O0OOOO0OO0OO .upper ()=='RELBASE1'):#line:229
                        O0O0OO00O0O00O00O ._opt_relbase1 =O0O00OO0OO00000O0 .get (OOOO0O0OOOO0OO0OO )#line:230
                    if (OOOO0O0OOOO0OO0OO .upper ()=='SCNDRELBASE')|(OOOO0O0OOOO0OO0OO .upper ()=='RELBASE2'):#line:231
                        O0O0OO00O0O00O00O ._opt_relbase2 =O0O00OO0OO00000O0 .get (OOOO0O0OOOO0OO0OO )#line:232
            else :#line:233
                print ("Warning: no quantifiers found. Optimization will not take place (1)")#line:234
        else :#line:235
            print ("Warning: no quantifiers found. Optimization will not take place (2)")#line:236
    def mine (OO0O0OO00O0O0O0OO ,**OO0OO0O00OOOO0O00 ):#line:239
        if not (OO0O0OO00O0O0O0OO ._initialized ):#line:240
            print ("Class NOT INITIALIZED. Please call constructor with dataframe first")#line:241
            return #line:242
        OO0O0OO00O0O0O0OO .kwargs =None #line:243
        if len (OO0OO0O00OOOO0O00 )>0 :#line:244
            OO0O0OO00O0O0O0OO .kwargs =OO0OO0O00OOOO0O00 #line:245
        OO0O0OO00O0O0O0OO ._init_task ()#line:246
        if len (OO0OO0O00OOOO0O00 )>0 :#line:247
            OOO0OOO0OO0OO0000 =OO0OO0O00OOOO0O00 .get ("proc",None )#line:248
            if not (OOO0OOO0OO0OO0000 ==None ):#line:249
                OO0O0OO00O0O0O0OO ._calc_all (**OO0OO0O00OOOO0O00 )#line:250
            else :#line:251
                print ("Rule mining procedure missing")#line:252
    def _get_ver (O00000OOO00O0O0OO ):#line:255
        return O00000OOO00O0O0OO .version_string #line:256
    def _print_disclaimer (OOOOOO000OOOO00OO ):#line:258
        print (f"Cleverminer version {OOOOOO000OOOO00OO._get_ver()}.")#line:260
    def _automatic_data_conversions (O0OOO0OO00O0O0000 ,OOO000OOO000OOOOO ):#line:266
        print ("Automatically reordering numeric categories ...")#line:267
        for OOO0O0O0O0OOO0O0O in range (len (OOO000OOO000OOOOO .columns )):#line:268
            if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:269
                print (f"#{OOO0O0O0O0OOO0O0O}: {OOO000OOO000OOOOO.columns[OOO0O0O0O0OOO0O0O]} : {OOO000OOO000OOOOO.dtypes[OOO0O0O0O0OOO0O0O]}.")#line:270
            try :#line:271
                OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]]=OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]].astype (str ).astype (float )#line:272
                if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:273
                    print (f"CONVERTED TO FLOATS #{OOO0O0O0O0OOO0O0O}: {OOO000OOO000OOOOO.columns[OOO0O0O0O0OOO0O0O]} : {OOO000OOO000OOOOO.dtypes[OOO0O0O0O0OOO0O0O]}.")#line:274
                OO0OO00OOO0O00000 =pd .unique (OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]])#line:275
                O0OO00OOOOO0OO0OO =True #line:276
                for OO0O00000OOO000O0 in OO0OO00OOO0O00000 :#line:277
                    if OO0O00000OOO000O0 %1 !=0 :#line:278
                        O0OO00OOOOO0OO0OO =False #line:279
                if O0OO00OOOOO0OO0OO :#line:280
                    OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]]=OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]].astype (int )#line:281
                    if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:282
                        print (f"CONVERTED TO INT #{OOO0O0O0O0OOO0O0O}: {OOO000OOO000OOOOO.columns[OOO0O0O0O0OOO0O0O]} : {OOO000OOO000OOOOO.dtypes[OOO0O0O0O0OOO0O0O]}.")#line:283
                OOO00O0OOO00OO000 =pd .unique (OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]])#line:284
                O000000O0OOO00O0O =CategoricalDtype (categories =OOO00O0OOO00OO000 .sort (),ordered =True )#line:285
                OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]]=OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]].astype (O000000O0OOO00O0O )#line:286
                if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:287
                    print (f"CONVERTED TO CATEGORY #{OOO0O0O0O0OOO0O0O}: {OOO000OOO000OOOOO.columns[OOO0O0O0O0OOO0O0O]} : {OOO000OOO000OOOOO.dtypes[OOO0O0O0O0OOO0O0O]}.")#line:288
            except :#line:290
                if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:291
                    print ("...cannot be converted to int")#line:292
                try :#line:293
                    O00OOO00000OOO0OO =OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]].unique ()#line:294
                    if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:295
                        print (f"Values: {O00OOO00000OOO0OO}")#line:296
                    OOOOO00OO0O0OO0OO =True #line:297
                    O000O00O0OO000O0O =[]#line:298
                    for OO0O00000OOO000O0 in O00OOO00000OOO0OO :#line:299
                        O000000OO000000O0 =re .findall (r"-?\d+",OO0O00000OOO000O0 )#line:302
                        if len (O000000OO000000O0 )>0 :#line:304
                            O000O00O0OO000O0O .append (int (O000000OO000000O0 [0 ]))#line:305
                        else :#line:306
                            OOOOO00OO0O0OO0OO =False #line:307
                    if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:308
                        print (f"Is ok: {OOOOO00OO0O0OO0OO}, extracted {O000O00O0OO000O0O}")#line:309
                    if OOOOO00OO0O0OO0OO :#line:310
                        O0OO000OOOOO0O0O0 =copy .deepcopy (O000O00O0OO000O0O )#line:311
                        O0OO000OOOOO0O0O0 .sort ()#line:312
                        OO0OOOOOO0O0OO0OO =[]#line:314
                        for OO0O0OO0000OOO00O in O0OO000OOOOO0O0O0 :#line:315
                            OO00O0OOOO00OOO0O =O000O00O0OO000O0O .index (OO0O0OO0000OOO00O )#line:316
                            OO0OOOOOO0O0OO0OO .append (O00OOO00000OOO0OO [OO00O0OOOO00OOO0O ])#line:318
                        if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:319
                            print (f"Sorted list: {OO0OOOOOO0O0OO0OO}")#line:320
                        O000000O0OOO00O0O =CategoricalDtype (categories =OO0OOOOOO0O0OO0OO ,ordered =True )#line:321
                        OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]]=OOO000OOO000OOOOO [OOO000OOO000OOOOO .columns [OOO0O0O0O0OOO0O0O ]].astype (O000000O0OOO00O0O )#line:322
                except :#line:325
                    if O0OOO0OO00O0O0000 .verbosity ['debug']:#line:326
                        print ("...cannot extract numbers from all categories")#line:327
    print ("Automatically reordering numeric categories ...done")#line:329
    def _prep_data (OOOOOOO000OOOOO00 ,OO0O00OOOO00000O0 ):#line:331
        print ("Starting data preparation ...")#line:332
        OOOOOOO000OOOOO00 ._init_data ()#line:333
        OOOOOOO000OOOOO00 .stats ['start_prep_time']=time .time ()#line:334
        if OOOOOOO000OOOOO00 .options ['automatic_data_conversions']:#line:335
            OOOOOOO000OOOOO00 ._automatic_data_conversions (OO0O00OOOO00000O0 )#line:336
        OOOOOOO000OOOOO00 .data ["rows_count"]=OO0O00OOOO00000O0 .shape [0 ]#line:337
        for OO0OOOOOO00OO00O0 in OO0O00OOOO00000O0 .select_dtypes (exclude =['category']).columns :#line:338
            OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ]=OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ].apply (str )#line:339
        try :#line:340
            OOOO0000O00O0O000 =pd .DataFrame .from_records ([(OOOOOOO00O00OO0OO ,OO0O00OOOO00000O0 [OOOOOOO00O00OO0OO ].nunique ())for OOOOOOO00O00OO0OO in OO0O00OOOO00000O0 .columns ],columns =['Column_Name','Num_Unique']).sort_values (by =['Num_Unique'])#line:342
        except :#line:343
            print ("Error in input data, probably unsupported data type. Will try to scan for column with unsupported type.")#line:344
            OO0O0O0OOOO00OO0O =""#line:345
            try :#line:346
                for OO0OOOOOO00OO00O0 in OO0O00OOOO00000O0 .columns :#line:347
                    OO0O0O0OOOO00OO0O =OO0OOOOOO00OO00O0 #line:348
                    print (f"...column {OO0OOOOOO00OO00O0} has {int(OO0O00OOOO00000O0[OO0OOOOOO00OO00O0].nunique())} values")#line:349
            except :#line:350
                print (f"... detected : column {OO0O0O0OOOO00OO0O} has unsupported type: {type(OO0O00OOOO00000O0[OO0OOOOOO00OO00O0])}.")#line:351
                exit (1 )#line:352
            print (f"Error in data profiling - attribute with unsupported type not detected. Please profile attributes manually, only simple attributes are supported.")#line:353
            exit (1 )#line:354
        if OOOOOOO000OOOOO00 .verbosity ['hint']:#line:357
            print ("Quick profile of input data: unique value counts are:")#line:358
            print (OOOO0000O00O0O000 )#line:359
            for OO0OOOOOO00OO00O0 in OO0O00OOOO00000O0 .columns :#line:360
                if OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ].nunique ()<OOOOOOO000OOOOO00 .options ['max_categories']:#line:361
                    OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ]=OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ].astype ('category')#line:362
                else :#line:363
                    print (f"WARNING: attribute {OO0OOOOOO00OO00O0} has more than {OOOOOOO000OOOOO00.options['max_categories']} values, will be ignored.\r\n If you haven't set maximum number of categories and you really need more categories and you know what you are doing, please use max_categories option to increase allowed number of categories.")#line:364
                    del OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ]#line:365
        for OO0OOOOOO00OO00O0 in OO0O00OOOO00000O0 .columns :#line:367
            if OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ].nunique ()>OOOOOOO000OOOOO00 .options ['max_categories']:#line:368
                print (f"WARNING: attribute {OO0OOOOOO00OO00O0} has more than {OOOOOOO000OOOOO00.options['max_categories']} values, will be ignored.\r\n If you haven't set maximum number of categories and you really need more categories and you know what you are doing, please use max_categories option to increase allowed number of categories.")#line:369
                del OO0O00OOOO00000O0 [OO0OOOOOO00OO00O0 ]#line:370
        if OOOOOOO000OOOOO00 .options ['keep_df']:#line:371
            if OOOOOOO000OOOOO00 .verbosity ['debug']:#line:372
                print ("Keeping df.")#line:373
            OOOOOOO000OOOOO00 .df =OO0O00OOOO00000O0 #line:374
        print ("Encoding columns into bit-form...")#line:375
        O0O0O0O00OOOOOO00 =0 #line:376
        OO0OO000OO0O00000 =0 #line:377
        for OOO0O00O0000OO0OO in OO0O00OOOO00000O0 :#line:378
            if OOOOOOO000OOOOO00 .verbosity ['debug']:#line:380
                print ('Column: '+OOO0O00O0000OO0OO )#line:381
            OOOOOOO000OOOOO00 .data ["varname"].append (OOO0O00O0000OO0OO )#line:382
            OOO000O0000O0O000 =pd .get_dummies (OO0O00OOOO00000O0 [OOO0O00O0000OO0OO ])#line:383
            OOOOOO0O000O000OO =0 #line:384
            if (OO0O00OOOO00000O0 .dtypes [OOO0O00O0000OO0OO ].name =='category'):#line:385
                OOOOOO0O000O000OO =1 #line:386
            OOOOOOO000OOOOO00 .data ["vtypes"].append (OOOOOO0O000O000OO )#line:387
            O00O0O000O00000OO =0 #line:390
            O0O0OOOO0O0000OOO =[]#line:391
            O000000000OO000O0 =[]#line:392
            for OOO0000OO0O0O0000 in OOO000O0000O0O000 :#line:394
                if OOOOOOO000OOOOO00 .verbosity ['debug']:#line:396
                    print ('....category : '+str (OOO0000OO0O0O0000 )+" @ "+str (time .time ()))#line:397
                O0O0OOOO0O0000OOO .append (OOO0000OO0O0O0000 )#line:398
                O00O000000O00OOOO =int (0 )#line:399
                OOO000O0000O000O0 =OOO000O0000O0O000 [OOO0000OO0O0O0000 ].values #line:400
                OO0OOOOO0O0OOOOO0 =numpy .packbits (OOO000O0000O000O0 ,bitorder ='little')#line:402
                O00O000000O00OOOO =int .from_bytes (OO0OOOOO0O0OOOOO0 ,byteorder ='little')#line:403
                O000000000OO000O0 .append (O00O000000O00OOOO )#line:404
                O00O0O000O00000OO +=1 #line:422
                OO0OO000OO0O00000 +=1 #line:423
            OOOOOOO000OOOOO00 .data ["catnames"].append (O0O0OOOO0O0000OOO )#line:425
            OOOOOOO000OOOOO00 .data ["dm"].append (O000000000OO000O0 )#line:426
        print ("Encoding columns into bit-form...done")#line:428
        if OOOOOOO000OOOOO00 .verbosity ['hint']:#line:429
            print (f"List of attributes for analysis is: {OOOOOOO000OOOOO00.data['varname']}")#line:430
            print (f"List of category names for individual attributes is : {OOOOOOO000OOOOO00.data['catnames']}")#line:431
        if OOOOOOO000OOOOO00 .verbosity ['debug']:#line:432
            print (f"List of vtypes is (all should be 1) : {OOOOOOO000OOOOO00.data['vtypes']}")#line:433
        OOOOOOO000OOOOO00 .data ["data_prepared"]=1 #line:435
        print ("Data preparation finished.")#line:436
        if OOOOOOO000OOOOO00 .verbosity ['debug']:#line:437
            print ('Number of variables : '+str (len (OOOOOOO000OOOOO00 .data ["dm"])))#line:438
            print ('Total number of categories in all variables : '+str (OO0OO000OO0O00000 ))#line:439
        OOOOOOO000OOOOO00 .stats ['end_prep_time']=time .time ()#line:440
        if OOOOOOO000OOOOO00 .verbosity ['debug']:#line:441
            print ('Time needed for data preparation : ',str (OOOOOOO000OOOOO00 .stats ['end_prep_time']-OOOOOOO000OOOOO00 .stats ['start_prep_time']))#line:442
    def _bitcount (OOOO00O0OOOO00O00 ,OOO0O00OOOOO000O0 ):#line:444
        OOO0OO00OOOO0O0O0 =None #line:445
        if (OOOO00O0OOOO00O00 ._is_py310 ):#line:446
            OOO0OO00OOOO0O0O0 =OOO0O00OOOOO000O0 .bit_count ()#line:447
        else :#line:448
            OOO0OO00OOOO0O0O0 =bin (OOO0O00OOOOO000O0 ).count ("1")#line:449
        return OOO0OO00OOOO0O0O0 #line:450
    def _verifyCF (O00OO0OO00O000000 ,_OOOO000OO00OOO000 ):#line:453
        O00O000OOOO0OOOOO =O00OO0OO00O000000 ._bitcount (_OOOO000OO00OOO000 )#line:454
        O000O0O0O00O0OOO0 =[]#line:455
        O00OO0O0O000OO0O0 =[]#line:456
        OO00OOOO0OOO0OOO0 =0 #line:457
        OOO0000O00OO0000O =0 #line:458
        OOOOOOO0O00O0OOO0 =0 #line:459
        O0OOO000O0000000O =0 #line:460
        OOOO000OO0O00000O =0 #line:461
        OOOO0O00O00OOOOOO =0 #line:462
        OO0000O0O0OO0O0OO =0 #line:463
        O00OO00OO00O00O0O =0 #line:464
        O0OO0000O00OO000O =0 #line:465
        OOO0O0O00O0OOOO0O =None #line:466
        OOOOOO00OO0O00OOO =None #line:467
        OOOOO00OO0OOO0OOO =None #line:468
        if ('min_step_size'in O00OO0OO00O000000 .quantifiers ):#line:469
            OOO0O0O00O0OOOO0O =O00OO0OO00O000000 .quantifiers .get ('min_step_size')#line:470
        if ('min_rel_step_size'in O00OO0OO00O000000 .quantifiers ):#line:471
            OOOOOO00OO0O00OOO =O00OO0OO00O000000 .quantifiers .get ('min_rel_step_size')#line:472
            if OOOOOO00OO0O00OOO >=1 and OOOOOO00OO0O00OOO <100 :#line:473
                OOOOOO00OO0O00OOO =OOOOOO00OO0O00OOO /100 #line:474
        O0O00O0O0OO00000O =0 #line:475
        O000O000O000OOO0O =0 #line:476
        OOOOOOO0OO0O0O0OO =[]#line:477
        if ('aad_weights'in O00OO0OO00O000000 .quantifiers ):#line:478
            O0O00O0O0OO00000O =1 #line:479
            OO00OO00OOO00000O =[]#line:480
            OOOOOOO0OO0O0O0OO =O00OO0OO00O000000 .quantifiers .get ('aad_weights')#line:481
        OO0O000OOO0O0O000 =O00OO0OO00O000000 .data ["dm"][O00OO0OO00O000000 .data ["varname"].index (O00OO0OO00O000000 .kwargs .get ('target'))]#line:482
        def O0OOOO00OOO000O0O (OOO000O0OOO00O0OO ,O000O0OOOOOO0O0O0 ):#line:483
            OOO0000O000O0000O =True #line:484
            if (OOO000O0OOO00O0OO >O000O0OOOOOO0O0O0 ):#line:485
                if not (OOO0O0O00O0OOOO0O is None or OOO000O0OOO00O0OO >=O000O0OOOOOO0O0O0 +OOO0O0O00O0OOOO0O ):#line:486
                    OOO0000O000O0000O =False #line:487
                if not (OOOOOO00OO0O00OOO is None or OOO000O0OOO00O0OO >=O000O0OOOOOO0O0O0 *(1 +OOOOOO00OO0O00OOO )):#line:488
                    OOO0000O000O0000O =False #line:489
            if (OOO000O0OOO00O0OO <O000O0OOOOOO0O0O0 ):#line:490
                if not (OOO0O0O00O0OOOO0O is None or OOO000O0OOO00O0OO <=O000O0OOOOOO0O0O0 -OOO0O0O00O0OOOO0O ):#line:491
                    OOO0000O000O0000O =False #line:492
                if not (OOOOOO00OO0O00OOO is None or OOO000O0OOO00O0OO <=O000O0OOOOOO0O0O0 *(1 -OOOOOO00OO0O00OOO )):#line:493
                    OOO0000O000O0000O =False #line:494
            return OOO0000O000O0000O #line:495
        for O0OO0O00OOOOOO0O0 in range (len (OO0O000OOO0O0O000 )):#line:496
            OOO0000O00OO0000O =OO00OOOO0OOO0OOO0 #line:498
            OO00OOOO0OOO0OOO0 =O00OO0OO00O000000 ._bitcount (_OOOO000OO00OOO000 &OO0O000OOO0O0O000 [O0OO0O00OOOOOO0O0 ])#line:499
            O000O0O0O00O0OOO0 .append (OO00OOOO0OOO0OOO0 )#line:500
            if O0OO0O00OOOOOO0O0 >0 :#line:501
                if (OO00OOOO0OOO0OOO0 >OOO0000O00OO0000O ):#line:502
                    if (OOOOOOO0O00O0OOO0 ==1 )and (O0OOOO00OOO000O0O (OO00OOOO0OOO0OOO0 ,OOO0000O00OO0000O )):#line:503
                        O00OO00OO00O00O0O +=1 #line:504
                    else :#line:505
                        if O0OOOO00OOO000O0O (OO00OOOO0OOO0OOO0 ,OOO0000O00OO0000O ):#line:506
                            O00OO00OO00O00O0O =1 #line:507
                        else :#line:508
                            O00OO00OO00O00O0O =0 #line:509
                    if O00OO00OO00O00O0O >O0OOO000O0000000O :#line:510
                        O0OOO000O0000000O =O00OO00OO00O00O0O #line:511
                    OOOOOOO0O00O0OOO0 =1 #line:512
                    if O0OOOO00OOO000O0O (OO00OOOO0OOO0OOO0 ,OOO0000O00OO0000O ):#line:513
                        OOOO0O00O00OOOOOO +=1 #line:514
                if (OO00OOOO0OOO0OOO0 <OOO0000O00OO0000O ):#line:515
                    if (OOOOOOO0O00O0OOO0 ==-1 )and (O0OOOO00OOO000O0O (OO00OOOO0OOO0OOO0 ,OOO0000O00OO0000O )):#line:516
                        O0OO0000O00OO000O +=1 #line:517
                    else :#line:518
                        if O0OOOO00OOO000O0O (OO00OOOO0OOO0OOO0 ,OOO0000O00OO0000O ):#line:519
                            O0OO0000O00OO000O =1 #line:520
                        else :#line:521
                            O0OO0000O00OO000O =0 #line:522
                    if O0OO0000O00OO000O >OOOO000OO0O00000O :#line:523
                        OOOO000OO0O00000O =O0OO0000O00OO000O #line:524
                    OOOOOOO0O00O0OOO0 =-1 #line:525
                    if O0OOOO00OOO000O0O (OO00OOOO0OOO0OOO0 ,OOO0000O00OO0000O ):#line:526
                        OO0000O0O0OO0O0OO +=1 #line:527
                if (OO00OOOO0OOO0OOO0 ==OOO0000O00OO0000O ):#line:528
                    OOOOOOO0O00O0OOO0 =0 #line:529
                    O0OO0000O00OO000O =0 #line:530
                    O00OO00OO00O00O0O =0 #line:531
            if (O0O00O0O0OO00000O ):#line:533
                OOO0000OO000OO000 =O00OO0OO00O000000 ._bitcount (OO0O000OOO0O0O000 [O0OO0O00OOOOOO0O0 ])#line:534
                OO00OO00OOO00000O .append (OOO0000OO000OO000 )#line:535
        if (O0O00O0O0OO00000O &sum (O000O0O0O00O0OOO0 )>0 ):#line:537
            for O0OO0O00OOOOOO0O0 in range (len (OO0O000OOO0O0O000 )):#line:538
                if OO00OO00OOO00000O [O0OO0O00OOOOOO0O0 ]>0 :#line:539
                    if O000O0O0O00O0OOO0 [O0OO0O00OOOOOO0O0 ]/sum (O000O0O0O00O0OOO0 )>OO00OO00OOO00000O [O0OO0O00OOOOOO0O0 ]/sum (OO00OO00OOO00000O ):#line:541
                        O000O000O000OOO0O +=OOOOOOO0OO0O0O0OO [O0OO0O00OOOOOO0O0 ]*((O000O0O0O00O0OOO0 [O0OO0O00OOOOOO0O0 ]/sum (O000O0O0O00O0OOO0 ))/(OO00OO00OOO00000O [O0OO0O00OOOOOO0O0 ]/sum (OO00OO00OOO00000O ))-1 )#line:542
        OO000OO0OOOO0OOO0 =True #line:545
        for O00OOO0O00OO0000O in O00OO0OO00O000000 .quantifiers .keys ():#line:546
            if O00OOO0O00OO0000O .upper ()=='BASE':#line:547
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=O00O000OOOO0OOOOO )#line:548
            if O00OOO0O00OO0000O .upper ()=='RELBASE':#line:549
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=O00O000OOOO0OOOOO *1.0 /O00OO0OO00O000000 .data ["rows_count"])#line:550
            if O00OOO0O00OO0000O .upper ()=='S_UP':#line:551
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=O0OOO000O0000000O )#line:552
            if O00OOO0O00OO0000O .upper ()=='S_DOWN':#line:553
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=OOOO000OO0O00000O )#line:554
            if O00OOO0O00OO0000O .upper ()=='S_ANY_UP':#line:555
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=O0OOO000O0000000O )#line:556
            if O00OOO0O00OO0000O .upper ()=='S_ANY_DOWN':#line:557
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=OOOO000OO0O00000O )#line:558
            if O00OOO0O00OO0000O .upper ()=='MAX':#line:559
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=max (O000O0O0O00O0OOO0 ))#line:560
            if O00OOO0O00OO0000O .upper ()=='MIN':#line:561
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=min (O000O0O0O00O0OOO0 ))#line:562
            if O00OOO0O00OO0000O .upper ()=='RELMAX':#line:563
                if sum (O000O0O0O00O0OOO0 )>0 :#line:564
                    OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=max (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 ))#line:565
                else :#line:566
                    OO000OO0OOOO0OOO0 =False #line:567
            if O00OOO0O00OO0000O .upper ()=='RELMAX_LEQ':#line:568
                if sum (O000O0O0O00O0OOO0 )>0 :#line:569
                    OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )>=max (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 ))#line:570
                else :#line:571
                    OO000OO0OOOO0OOO0 =False #line:572
            if O00OOO0O00OO0000O .upper ()=='RELMIN':#line:573
                if sum (O000O0O0O00O0OOO0 )>0 :#line:574
                    OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=min (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 ))#line:575
                else :#line:576
                    OO000OO0OOOO0OOO0 =False #line:577
            if O00OOO0O00OO0000O .upper ()=='RELMIN_LEQ':#line:578
                if sum (O000O0O0O00O0OOO0 )>0 :#line:579
                    OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )>=min (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 ))#line:580
                else :#line:581
                    OO000OO0OOOO0OOO0 =False #line:582
            if O00OOO0O00OO0000O .upper ()=='AAD':#line:583
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )<=O000O000O000OOO0O )#line:584
            if O00OOO0O00OO0000O .upper ()=='RELRANGE_LEQ':#line:586
                O0OO00000OOO0OOOO =O00OO0OO00O000000 .quantifiers .get (O00OOO0O00OO0000O )#line:587
                if O0OO00000OOO0OOOO >=1 and O0OO00000OOO0OOOO <100 :#line:588
                    O0OO00000OOO0OOOO =O0OO00000OOO0OOOO *1.0 /100 #line:589
                O0000OO0OOO00OOOO =min (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 )#line:590
                O0OO000O00000OOOO =max (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 )#line:591
                OO000OO0OOOO0OOO0 =OO000OO0OOOO0OOO0 and (O0OO00000OOO0OOOO >=O0OO000O00000OOOO -O0000OO0OOO00OOOO )#line:592
        OO0O00O00O0000O00 ={}#line:593
        if OO000OO0OOOO0OOO0 ==True :#line:594
            O00OO0OO00O000000 .stats ['total_valid']+=1 #line:596
            OO0O00O00O0000O00 ["base"]=O00O000OOOO0OOOOO #line:597
            OO0O00O00O0000O00 ["rel_base"]=O00O000OOOO0OOOOO *1.0 /O00OO0OO00O000000 .data ["rows_count"]#line:598
            OO0O00O00O0000O00 ["s_up"]=O0OOO000O0000000O #line:599
            OO0O00O00O0000O00 ["s_down"]=OOOO000OO0O00000O #line:600
            OO0O00O00O0000O00 ["s_any_up"]=OOOO0O00O00OOOOOO #line:601
            OO0O00O00O0000O00 ["s_any_down"]=OO0000O0O0OO0O0OO #line:602
            OO0O00O00O0000O00 ["max"]=max (O000O0O0O00O0OOO0 )#line:603
            OO0O00O00O0000O00 ["min"]=min (O000O0O0O00O0OOO0 )#line:604
            if sum (O000O0O0O00O0OOO0 )>0 :#line:607
                OO0O00O00O0000O00 ["rel_max"]=max (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 )#line:608
                OO0O00O00O0000O00 ["rel_min"]=min (O000O0O0O00O0OOO0 )*1.0 /sum (O000O0O0O00O0OOO0 )#line:609
            else :#line:610
                OO0O00O00O0000O00 ["rel_max"]=0 #line:611
                OO0O00O00O0000O00 ["rel_min"]=0 #line:612
            OO0O00O00O0000O00 ["hist"]=O000O0O0O00O0OOO0 #line:613
            if O0O00O0O0OO00000O :#line:614
                OO0O00O00O0000O00 ["aad"]=O000O000O000OOO0O #line:615
                OO0O00O00O0000O00 ["hist_full"]=OO00OO00OOO00000O #line:616
                OO0O00O00O0000O00 ["rel_hist"]=[O0OOO0000O000OO0O /sum (O000O0O0O00O0OOO0 )for O0OOO0000O000OO0O in O000O0O0O00O0OOO0 ]#line:617
                OO0O00O00O0000O00 ["rel_hist_full"]=[OO00OOOO0OOOO000O /sum (OO00OO00OOO00000O )for OO00OOOO0OOOO000O in OO00OO00OOO00000O ]#line:618
        return OO000OO0OOOO0OOO0 ,OO0O00O00O0000O00 #line:620
    def _verifyUIC (OO0OO0OOO00OO0OOO ,_O000O0OO000O0O000 ):#line:622
        O00O000O0000000OO ={}#line:623
        OO0OO00000O0O0000 =0 #line:624
        for OOOO00O0OO0OOO0OO in OO0OO0OOO00OO0OOO .task_actinfo ['cedents']:#line:625
            O00O000O0000000OO [OOOO00O0OO0OOO0OO ['cedent_type']]=OOOO00O0OO0OOO0OO ['filter_value']#line:627
            OO0OO00000O0O0000 =OO0OO00000O0O0000 +1 #line:628
        OO000OOOO0OOO0O0O =OO0OO0OOO00OO0OOO ._bitcount (_O000O0OO000O0O000 )#line:630
        O0O00OO00O0O00000 =[]#line:631
        OOOO0000O0O000O0O =0 #line:632
        O0OOO0O00O0000O0O =0 #line:633
        O000000O0O0000O0O =0 #line:634
        O00O00O0OO00OOOOO =[]#line:635
        OO0O0OO0OOO00000O =[]#line:636
        if ('aad_weights'in OO0OO0OOO00OO0OOO .quantifiers ):#line:637
            O00O00O0OO00OOOOO =OO0OO0OOO00OO0OOO .quantifiers .get ('aad_weights')#line:638
            O0OOO0O00O0000O0O =1 #line:639
        O000O00OO0O00OO00 =OO0OO0OOO00OO0OOO .data ["dm"][OO0OO0OOO00OO0OOO .data ["varname"].index (OO0OO0OOO00OO0OOO .kwargs .get ('target'))]#line:640
        for O0OO0OOO0OO0O00O0 in range (len (O000O00OO0O00OO00 )):#line:641
            OOO00O000O0OO00O0 =OOOO0000O0O000O0O #line:643
            OOOO0000O0O000O0O =OO0OO0OOO00OO0OOO ._bitcount (_O000O0OO000O0O000 &O000O00OO0O00OO00 [O0OO0OOO0OO0O00O0 ])#line:644
            O0O00OO00O0O00000 .append (OOOO0000O0O000O0O )#line:645
            O0OO0OO000000OOOO =OO0OO0OOO00OO0OOO ._bitcount (O00O000O0000000OO ['cond']&O000O00OO0O00OO00 [O0OO0OOO0OO0O00O0 ])#line:648
            OO0O0OO0OOO00000O .append (O0OO0OO000000OOOO )#line:649
        if (O0OOO0O00O0000O0O &sum (O0O00OO00O0O00000 )>0 ):#line:651
            for O0OO0OOO0OO0O00O0 in range (len (O000O00OO0O00OO00 )):#line:652
                if OO0O0OO0OOO00000O [O0OO0OOO0OO0O00O0 ]>0 :#line:653
                    if O0O00OO00O0O00000 [O0OO0OOO0OO0O00O0 ]/sum (O0O00OO00O0O00000 )>OO0O0OO0OOO00000O [O0OO0OOO0OO0O00O0 ]/sum (OO0O0OO0OOO00000O ):#line:655
                        O000000O0O0000O0O +=O00O00O0OO00OOOOO [O0OO0OOO0OO0O00O0 ]*((O0O00OO00O0O00000 [O0OO0OOO0OO0O00O0 ]/sum (O0O00OO00O0O00000 ))/(OO0O0OO0OOO00000O [O0OO0OOO0OO0O00O0 ]/sum (OO0O0OO0OOO00000O ))-1 )#line:656
        O00O0O00OO0OO0OO0 =True #line:659
        for O0OOO0O000OO00OOO in OO0OO0OOO00OO0OOO .quantifiers .keys ():#line:660
            if O0OOO0O000OO00OOO .upper ()=='BASE':#line:661
                O00O0O00OO0OO0OO0 =O00O0O00OO0OO0OO0 and (OO0OO0OOO00OO0OOO .quantifiers .get (O0OOO0O000OO00OOO )<=OO000OOOO0OOO0O0O )#line:662
            if O0OOO0O000OO00OOO .upper ()=='RELBASE':#line:663
                O00O0O00OO0OO0OO0 =O00O0O00OO0OO0OO0 and (OO0OO0OOO00OO0OOO .quantifiers .get (O0OOO0O000OO00OOO )<=OO000OOOO0OOO0O0O *1.0 /OO0OO0OOO00OO0OOO .data ["rows_count"])#line:664
            if O0OOO0O000OO00OOO .upper ()=='AAD_SCORE':#line:665
                O00O0O00OO0OO0OO0 =O00O0O00OO0OO0OO0 and (OO0OO0OOO00OO0OOO .quantifiers .get (O0OOO0O000OO00OOO )<=O000000O0O0000O0O )#line:666
        OO0O000OOOO0O0OO0 ={}#line:668
        if O00O0O00OO0OO0OO0 ==True :#line:669
            OO0OO0OOO00OO0OOO .stats ['total_valid']+=1 #line:671
            OO0O000OOOO0O0OO0 ["base"]=OO000OOOO0OOO0O0O #line:672
            OO0O000OOOO0O0OO0 ["rel_base"]=OO000OOOO0OOO0O0O *1.0 /OO0OO0OOO00OO0OOO .data ["rows_count"]#line:673
            OO0O000OOOO0O0OO0 ["hist"]=O0O00OO00O0O00000 #line:674
            OO0O000OOOO0O0OO0 ["aad_score"]=O000000O0O0000O0O #line:676
            OO0O000OOOO0O0OO0 ["hist_cond"]=OO0O0OO0OOO00000O #line:677
            OO0O000OOOO0O0OO0 ["rel_hist"]=[O00O0OOO0OO0000OO /sum (O0O00OO00O0O00000 )for O00O0OOO0OO0000OO in O0O00OO00O0O00000 ]#line:678
            OO0O000OOOO0O0OO0 ["rel_hist_cond"]=[O0O0OOOO0OO0O0OOO /sum (OO0O0OO0OOO00000O )for O0O0OOOO0OO0O0OOO in OO0O0OO0OOO00000O ]#line:679
        return O00O0O00OO0OO0OO0 ,OO0O000OOOO0O0OO0 #line:681
    def _verify4ft (O0OO0O00OO000OOOO ,_O0OO0000O00O000OO ):#line:683
        OOO0O0O000O0O0OOO ={}#line:684
        OO0OOO0O000O0OOOO =0 #line:685
        for O0OO00OO0OO0O0OOO in O0OO0O00OO000OOOO .task_actinfo ['cedents']:#line:686
            OOO0O0O000O0O0OOO [O0OO00OO0OO0O0OOO ['cedent_type']]=O0OO00OO0OO0O0OOO ['filter_value']#line:688
            OO0OOO0O000O0OOOO =OO0OOO0O000O0OOOO +1 #line:689
        OOOO000O00O00O00O =O0OO0O00OO000OOOO ._bitcount (OOO0O0O000O0O0OOO ['ante']&OOO0O0O000O0O0OOO ['succ']&OOO0O0O000O0O0OOO ['cond'])#line:691
        O000OOO0O0000O00O =None #line:692
        O000OOO0O0000O00O =0 #line:693
        if OOOO000O00O00O00O >0 :#line:702
            O000OOO0O0000O00O =O0OO0O00OO000OOOO ._bitcount (OOO0O0O000O0O0OOO ['ante']&OOO0O0O000O0O0OOO ['succ']&OOO0O0O000O0O0OOO ['cond'])*1.0 /O0OO0O00OO000OOOO ._bitcount (OOO0O0O000O0O0OOO ['ante']&OOO0O0O000O0O0OOO ['cond'])#line:703
        OOOOOOO0000OO000O =1 <<O0OO0O00OO000OOOO .data ["rows_count"]#line:705
        OOOO0OO0OOO000OOO =O0OO0O00OO000OOOO ._bitcount (OOO0O0O000O0O0OOO ['ante']&OOO0O0O000O0O0OOO ['succ']&OOO0O0O000O0O0OOO ['cond'])#line:706
        OOO0O0OOOOOO00OO0 =O0OO0O00OO000OOOO ._bitcount (OOO0O0O000O0O0OOO ['ante']&~(OOOOOOO0000OO000O |OOO0O0O000O0O0OOO ['succ'])&OOO0O0O000O0O0OOO ['cond'])#line:707
        O0OO00OO0OO0O0OOO =O0OO0O00OO000OOOO ._bitcount (~(OOOOOOO0000OO000O |OOO0O0O000O0O0OOO ['ante'])&OOO0O0O000O0O0OOO ['succ']&OOO0O0O000O0O0OOO ['cond'])#line:708
        OO0OO0O00OO00OOOO =O0OO0O00OO000OOOO ._bitcount (~(OOOOOOO0000OO000O |OOO0O0O000O0O0OOO ['ante'])&~(OOOOOOO0000OO000O |OOO0O0O000O0O0OOO ['succ'])&OOO0O0O000O0O0OOO ['cond'])#line:709
        OOOOO0O0O00O0OO0O =0 #line:710
        if (OOOO0OO0OOO000OOO +OOO0O0OOOOOO00OO0 )*(OOOO0OO0OOO000OOO +O0OO00OO0OO0O0OOO )>0 :#line:711
            OOOOO0O0O00O0OO0O =OOOO0OO0OOO000OOO *(OOOO0OO0OOO000OOO +OOO0O0OOOOOO00OO0 +O0OO00OO0OO0O0OOO +OO0OO0O00OO00OOOO )/(OOOO0OO0OOO000OOO +OOO0O0OOOOOO00OO0 )/(OOOO0OO0OOO000OOO +O0OO00OO0OO0O0OOO )-1 #line:712
        else :#line:713
            OOOOO0O0O00O0OO0O =None #line:714
        O0O0OOO00O0OOO00O =0 #line:715
        if (OOOO0OO0OOO000OOO +OOO0O0OOOOOO00OO0 )*(OOOO0OO0OOO000OOO +O0OO00OO0OO0O0OOO )>0 :#line:716
            O0O0OOO00O0OOO00O =1 -OOOO0OO0OOO000OOO *(OOOO0OO0OOO000OOO +OOO0O0OOOOOO00OO0 +O0OO00OO0OO0O0OOO +OO0OO0O00OO00OOOO )/(OOOO0OO0OOO000OOO +OOO0O0OOOOOO00OO0 )/(OOOO0OO0OOO000OOO +O0OO00OO0OO0O0OOO )#line:717
        else :#line:718
            O0O0OOO00O0OOO00O =None #line:719
        O00O0000OO0000OO0 =True #line:720
        for OOO0000000O0O0000 in O0OO0O00OO000OOOO .quantifiers .keys ():#line:721
            if OOO0000000O0O0000 .upper ()=='BASE':#line:722
                O00O0000OO0000OO0 =O00O0000OO0000OO0 and (O0OO0O00OO000OOOO .quantifiers .get (OOO0000000O0O0000 )<=OOOO000O00O00O00O )#line:723
            if OOO0000000O0O0000 .upper ()=='RELBASE':#line:724
                O00O0000OO0000OO0 =O00O0000OO0000OO0 and (O0OO0O00OO000OOOO .quantifiers .get (OOO0000000O0O0000 )<=OOOO000O00O00O00O *1.0 /O0OO0O00OO000OOOO .data ["rows_count"])#line:725
            if (OOO0000000O0O0000 .upper ()=='PIM')or (OOO0000000O0O0000 .upper ()=='CONF'):#line:726
                O00O0000OO0000OO0 =O00O0000OO0000OO0 and (O0OO0O00OO000OOOO .quantifiers .get (OOO0000000O0O0000 )<=O000OOO0O0000O00O )#line:727
            if OOO0000000O0O0000 .upper ()=='AAD':#line:728
                if OOOOO0O0O00O0OO0O !=None :#line:729
                    O00O0000OO0000OO0 =O00O0000OO0000OO0 and (O0OO0O00OO000OOOO .quantifiers .get (OOO0000000O0O0000 )<=OOOOO0O0O00O0OO0O )#line:730
                else :#line:731
                    O00O0000OO0000OO0 =False #line:732
            if OOO0000000O0O0000 .upper ()=='BAD':#line:733
                if O0O0OOO00O0OOO00O !=None :#line:734
                    O00O0000OO0000OO0 =O00O0000OO0000OO0 and (O0OO0O00OO000OOOO .quantifiers .get (OOO0000000O0O0000 )<=O0O0OOO00O0OOO00O )#line:735
                else :#line:736
                    O00O0000OO0000OO0 =False #line:737
            O0OO000000OOO00OO ={}#line:738
        if O00O0000OO0000OO0 ==True :#line:739
            O0OO0O00OO000OOOO .stats ['total_valid']+=1 #line:741
            O0OO000000OOO00OO ["base"]=OOOO000O00O00O00O #line:742
            O0OO000000OOO00OO ["rel_base"]=OOOO000O00O00O00O *1.0 /O0OO0O00OO000OOOO .data ["rows_count"]#line:743
            O0OO000000OOO00OO ["conf"]=O000OOO0O0000O00O #line:744
            O0OO000000OOO00OO ["aad"]=OOOOO0O0O00O0OO0O #line:745
            O0OO000000OOO00OO ["bad"]=O0O0OOO00O0OOO00O #line:746
            O0OO000000OOO00OO ["fourfold"]=[OOOO0OO0OOO000OOO ,OOO0O0OOOOOO00OO0 ,O0OO00OO0OO0O0OOO ,OO0OO0O00OO00OOOO ]#line:747
        return O00O0000OO0000OO0 ,O0OO000000OOO00OO #line:751
    def _verifysd4ft (O00000O0O00OOOOOO ,_OO0O00OO00000O0OO ):#line:753
        O000O00000000OO00 ={}#line:754
        OOOO0OO0000O0OO00 =0 #line:755
        for O0O0O00O00000O0O0 in O00000O0O00OOOOOO .task_actinfo ['cedents']:#line:756
            O000O00000000OO00 [O0O0O00O00000O0O0 ['cedent_type']]=O0O0O00O00000O0O0 ['filter_value']#line:758
            OOOO0OO0000O0OO00 =OOOO0OO0000O0OO00 +1 #line:759
        O0O00O0O0O0000OO0 =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['frst'])#line:761
        O0O0O00OO0000O000 =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['scnd'])#line:762
        O0OO000000O0O00OO =None #line:763
        O0OOOOOO00OOO0O0O =0 #line:764
        OOOO000OOO00O000O =0 #line:765
        if O0O00O0O0O0000OO0 >0 :#line:774
            O0OOOOOO00OOO0O0O =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['frst'])*1.0 /O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['frst'])#line:775
        if O0O0O00OO0000O000 >0 :#line:776
            OOOO000OOO00O000O =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['scnd'])*1.0 /O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['scnd'])#line:777
        O0OO0O0000OOOO000 =1 <<O00000O0O00OOOOOO .data ["rows_count"]#line:779
        O0O0OOOOO00O0OOO0 =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['frst'])#line:780
        O0OOO000O0OOO0OO0 =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&~(O0OO0O0000OOOO000 |O000O00000000OO00 ['succ'])&O000O00000000OO00 ['cond']&O000O00000000OO00 ['frst'])#line:781
        OO0OOO00000O0OOO0 =O00000O0O00OOOOOO ._bitcount (~(O0OO0O0000OOOO000 |O000O00000000OO00 ['ante'])&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['frst'])#line:782
        OOO0O000O0O0O0O00 =O00000O0O00OOOOOO ._bitcount (~(O0OO0O0000OOOO000 |O000O00000000OO00 ['ante'])&~(O0OO0O0000OOOO000 |O000O00000000OO00 ['succ'])&O000O00000000OO00 ['cond']&O000O00000000OO00 ['frst'])#line:783
        OO0O0OOO0000O0000 =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['scnd'])#line:784
        O0OOOO00O0OO00O0O =O00000O0O00OOOOOO ._bitcount (O000O00000000OO00 ['ante']&~(O0OO0O0000OOOO000 |O000O00000000OO00 ['succ'])&O000O00000000OO00 ['cond']&O000O00000000OO00 ['scnd'])#line:785
        OO000000OOOO0O0OO =O00000O0O00OOOOOO ._bitcount (~(O0OO0O0000OOOO000 |O000O00000000OO00 ['ante'])&O000O00000000OO00 ['succ']&O000O00000000OO00 ['cond']&O000O00000000OO00 ['scnd'])#line:786
        OO000O00O000O0O0O =O00000O0O00OOOOOO ._bitcount (~(O0OO0O0000OOOO000 |O000O00000000OO00 ['ante'])&~(O0OO0O0000OOOO000 |O000O00000000OO00 ['succ'])&O000O00000000OO00 ['cond']&O000O00000000OO00 ['scnd'])#line:787
        OOOOO0OOO0O0OO0OO =True #line:788
        for OOOOO0O0OO0OO0000 in O00000O0O00OOOOOO .quantifiers .keys ():#line:789
            if (OOOOO0O0OO0OO0000 .upper ()=='FRSTBASE')|(OOOOO0O0OO0OO0000 .upper ()=='BASE1'):#line:790
                OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=O0O00O0O0O0000OO0 )#line:791
            if (OOOOO0O0OO0OO0000 .upper ()=='SCNDBASE')|(OOOOO0O0OO0OO0000 .upper ()=='BASE2'):#line:792
                OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=O0O0O00OO0000O000 )#line:793
            if (OOOOO0O0OO0OO0000 .upper ()=='FRSTRELBASE')|(OOOOO0O0OO0OO0000 .upper ()=='RELBASE1'):#line:794
                OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=O0O00O0O0O0000OO0 *1.0 /O00000O0O00OOOOOO .data ["rows_count"])#line:795
            if (OOOOO0O0OO0OO0000 .upper ()=='SCNDRELBASE')|(OOOOO0O0OO0OO0000 .upper ()=='RELBASE2'):#line:796
                OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=O0O0O00OO0000O000 *1.0 /O00000O0O00OOOOOO .data ["rows_count"])#line:797
            if (OOOOO0O0OO0OO0000 .upper ()=='FRSTPIM')|(OOOOO0O0OO0OO0000 .upper ()=='PIM1')|(OOOOO0O0OO0OO0000 .upper ()=='FRSTCONF')|(OOOOO0O0OO0OO0000 .upper ()=='CONF1'):#line:798
                OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=O0OOOOOO00OOO0O0O )#line:799
            if (OOOOO0O0OO0OO0000 .upper ()=='SCNDPIM')|(OOOOO0O0OO0OO0000 .upper ()=='PIM2')|(OOOOO0O0OO0OO0000 .upper ()=='SCNDCONF')|(OOOOO0O0OO0OO0000 .upper ()=='CONF2'):#line:800
                OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=OOOO000OOO00O000O )#line:801
            if (OOOOO0O0OO0OO0000 .upper ()=='DELTAPIM')|(OOOOO0O0OO0OO0000 .upper ()=='DELTACONF'):#line:802
                OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=O0OOOOOO00OOO0O0O -OOOO000OOO00O000O )#line:803
            if (OOOOO0O0OO0OO0000 .upper ()=='RATIOPIM')|(OOOOO0O0OO0OO0000 .upper ()=='RATIOCONF'):#line:806
                if (OOOO000OOO00O000O >0 ):#line:807
                    OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )<=O0OOOOOO00OOO0O0O *1.0 /OOOO000OOO00O000O )#line:808
                else :#line:809
                    OOOOO0OOO0O0OO0OO =False #line:810
            if (OOOOO0O0OO0OO0000 .upper ()=='RATIOPIM_LEQ')|(OOOOO0O0OO0OO0000 .upper ()=='RATIOCONF_LEQ'):#line:811
                if (OOOO000OOO00O000O >0 ):#line:812
                    OOOOO0OOO0O0OO0OO =OOOOO0OOO0O0OO0OO and (O00000O0O00OOOOOO .quantifiers .get (OOOOO0O0OO0OO0000 )>=O0OOOOOO00OOO0O0O *1.0 /OOOO000OOO00O000O )#line:813
                else :#line:814
                    OOOOO0OOO0O0OO0OO =False #line:815
        OO0000O0000000000 ={}#line:816
        if OOOOO0OOO0O0OO0OO ==True :#line:817
            O00000O0O00OOOOOO .stats ['total_valid']+=1 #line:819
            OO0000O0000000000 ["base1"]=O0O00O0O0O0000OO0 #line:820
            OO0000O0000000000 ["base2"]=O0O0O00OO0000O000 #line:821
            OO0000O0000000000 ["rel_base1"]=O0O00O0O0O0000OO0 *1.0 /O00000O0O00OOOOOO .data ["rows_count"]#line:822
            OO0000O0000000000 ["rel_base2"]=O0O0O00OO0000O000 *1.0 /O00000O0O00OOOOOO .data ["rows_count"]#line:823
            OO0000O0000000000 ["conf1"]=O0OOOOOO00OOO0O0O #line:824
            OO0000O0000000000 ["conf2"]=OOOO000OOO00O000O #line:825
            OO0000O0000000000 ["deltaconf"]=O0OOOOOO00OOO0O0O -OOOO000OOO00O000O #line:826
            if (OOOO000OOO00O000O >0 ):#line:827
                OO0000O0000000000 ["ratioconf"]=O0OOOOOO00OOO0O0O *1.0 /OOOO000OOO00O000O #line:828
            else :#line:829
                OO0000O0000000000 ["ratioconf"]=None #line:830
            OO0000O0000000000 ["fourfold1"]=[O0O0OOOOO00O0OOO0 ,O0OOO000O0OOO0OO0 ,OO0OOO00000O0OOO0 ,OOO0O000O0O0O0O00 ]#line:831
            OO0000O0000000000 ["fourfold2"]=[OO0O0OOO0000O0000 ,O0OOOO00O0OO00O0O ,OO000000OOOO0O0OO ,OO000O00O000O0O0O ]#line:832
        return OOOOO0OOO0O0OO0OO ,OO0000O0000000000 #line:836
    def _verifynewact4ft (O0O00000OO0000O00 ,_O0O00O00OOO0OO00O ):#line:838
        OO0OO00O0O0OOO0OO ={}#line:839
        for OOO00OOO00O000000 in O0O00000OO0000O00 .task_actinfo ['cedents']:#line:840
            OO0OO00O0O0OOO0OO [OOO00OOO00O000000 ['cedent_type']]=OOO00OOO00O000000 ['filter_value']#line:842
        OOO0OOOOO0O0OO0OO =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond'])#line:844
        O0O0000OOO00O00O0 =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond']&OO0OO00O0O0OOO0OO ['antv']&OO0OO00O0O0OOO0OO ['sucv'])#line:845
        OO0OOO00OOO00O000 =None #line:846
        OO00OOOO0O000OOOO =0 #line:847
        OO0OOO0O0000OOOO0 =0 #line:848
        if OOO0OOOOO0O0OO0OO >0 :#line:857
            OO00OOOO0O000OOOO =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond'])*1.0 /O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['cond'])#line:858
        if O0O0000OOO00O00O0 >0 :#line:859
            OO0OOO0O0000OOOO0 =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond']&OO0OO00O0O0OOO0OO ['antv']&OO0OO00O0O0OOO0OO ['sucv'])*1.0 /O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['cond']&OO0OO00O0O0OOO0OO ['antv'])#line:861
        O0OOO00O0O0O000OO =1 <<O0O00000OO0000O00 .rows_count #line:863
        O00O000OOOOO00OO0 =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond'])#line:864
        O0O00OOO00OO0OO0O =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&~(O0OOO00O0O0O000OO |OO0OO00O0O0OOO0OO ['succ'])&OO0OO00O0O0OOO0OO ['cond'])#line:865
        O000O0O0OOOO0000O =O0O00000OO0000O00 ._bitcount (~(O0OOO00O0O0O000OO |OO0OO00O0O0OOO0OO ['ante'])&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond'])#line:866
        OOOOO0OO0O00O000O =O0O00000OO0000O00 ._bitcount (~(O0OOO00O0O0O000OO |OO0OO00O0O0OOO0OO ['ante'])&~(O0OOO00O0O0O000OO |OO0OO00O0O0OOO0OO ['succ'])&OO0OO00O0O0OOO0OO ['cond'])#line:867
        OOO000O00OO000O00 =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond']&OO0OO00O0O0OOO0OO ['antv']&OO0OO00O0O0OOO0OO ['sucv'])#line:868
        OOOOO0O00O0O0OOOO =O0O00000OO0000O00 ._bitcount (OO0OO00O0O0OOO0OO ['ante']&~(O0OOO00O0O0O000OO |(OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['sucv']))&OO0OO00O0O0OOO0OO ['cond'])#line:869
        OO000O0000O0O000O =O0O00000OO0000O00 ._bitcount (~(O0OOO00O0O0O000OO |(OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['antv']))&OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['cond']&OO0OO00O0O0OOO0OO ['sucv'])#line:870
        O0O0O00OOOO0000OO =O0O00000OO0000O00 ._bitcount (~(O0OOO00O0O0O000OO |(OO0OO00O0O0OOO0OO ['ante']&OO0OO00O0O0OOO0OO ['antv']))&~(O0OOO00O0O0O000OO |(OO0OO00O0O0OOO0OO ['succ']&OO0OO00O0O0OOO0OO ['sucv']))&OO0OO00O0O0OOO0OO ['cond'])#line:871
        O00O00OO0000O0O00 =True #line:872
        for O0OO0O0OOO00OOOOO in O0O00000OO0000O00 .quantifiers .keys ():#line:873
            if (O0OO0O0OOO00OOOOO =='PreBase')|(O0OO0O0OOO00OOOOO =='Base1'):#line:874
                O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=OOO0OOOOO0O0OO0OO )#line:875
            if (O0OO0O0OOO00OOOOO =='PostBase')|(O0OO0O0OOO00OOOOO =='Base2'):#line:876
                O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=O0O0000OOO00O00O0 )#line:877
            if (O0OO0O0OOO00OOOOO =='PreRelBase')|(O0OO0O0OOO00OOOOO =='RelBase1'):#line:878
                O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=OOO0OOOOO0O0OO0OO *1.0 /O0O00000OO0000O00 .data ["rows_count"])#line:879
            if (O0OO0O0OOO00OOOOO =='PostRelBase')|(O0OO0O0OOO00OOOOO =='RelBase2'):#line:880
                O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=O0O0000OOO00O00O0 *1.0 /O0O00000OO0000O00 .data ["rows_count"])#line:881
            if (O0OO0O0OOO00OOOOO =='Prepim')|(O0OO0O0OOO00OOOOO =='pim1')|(O0OO0O0OOO00OOOOO =='PreConf')|(O0OO0O0OOO00OOOOO =='conf1'):#line:882
                O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=OO00OOOO0O000OOOO )#line:883
            if (O0OO0O0OOO00OOOOO =='Postpim')|(O0OO0O0OOO00OOOOO =='pim2')|(O0OO0O0OOO00OOOOO =='PostConf')|(O0OO0O0OOO00OOOOO =='conf2'):#line:884
                O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=OO0OOO0O0000OOOO0 )#line:885
            if (O0OO0O0OOO00OOOOO =='Deltapim')|(O0OO0O0OOO00OOOOO =='DeltaConf'):#line:886
                O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=OO00OOOO0O000OOOO -OO0OOO0O0000OOOO0 )#line:887
            if (O0OO0O0OOO00OOOOO =='Ratiopim')|(O0OO0O0OOO00OOOOO =='RatioConf'):#line:890
                if (OO0OOO0O0000OOOO0 >0 ):#line:891
                    O00O00OO0000O0O00 =O00O00OO0000O0O00 and (O0O00000OO0000O00 .quantifiers .get (O0OO0O0OOO00OOOOO )<=OO00OOOO0O000OOOO *1.0 /OO0OOO0O0000OOOO0 )#line:892
                else :#line:893
                    O00O00OO0000O0O00 =False #line:894
        OO0OO0O0O0OO0000O ={}#line:895
        if O00O00OO0000O0O00 ==True :#line:896
            O0O00000OO0000O00 .stats ['total_valid']+=1 #line:898
            OO0OO0O0O0OO0000O ["base1"]=OOO0OOOOO0O0OO0OO #line:899
            OO0OO0O0O0OO0000O ["base2"]=O0O0000OOO00O00O0 #line:900
            OO0OO0O0O0OO0000O ["rel_base1"]=OOO0OOOOO0O0OO0OO *1.0 /O0O00000OO0000O00 .data ["rows_count"]#line:901
            OO0OO0O0O0OO0000O ["rel_base2"]=O0O0000OOO00O00O0 *1.0 /O0O00000OO0000O00 .data ["rows_count"]#line:902
            OO0OO0O0O0OO0000O ["conf1"]=OO00OOOO0O000OOOO #line:903
            OO0OO0O0O0OO0000O ["conf2"]=OO0OOO0O0000OOOO0 #line:904
            OO0OO0O0O0OO0000O ["deltaconf"]=OO00OOOO0O000OOOO -OO0OOO0O0000OOOO0 #line:905
            if (OO0OOO0O0000OOOO0 >0 ):#line:906
                OO0OO0O0O0OO0000O ["ratioconf"]=OO00OOOO0O000OOOO *1.0 /OO0OOO0O0000OOOO0 #line:907
            else :#line:908
                OO0OO0O0O0OO0000O ["ratioconf"]=None #line:909
            OO0OO0O0O0OO0000O ["fourfoldpre"]=[O00O000OOOOO00OO0 ,O0O00OOO00OO0OO0O ,O000O0O0OOOO0000O ,OOOOO0OO0O00O000O ]#line:910
            OO0OO0O0O0OO0000O ["fourfoldpost"]=[OOO000O00OO000O00 ,OOOOO0O00O0O0OOOO ,OO000O0000O0O000O ,O0O0O00OOOO0000OO ]#line:911
        return O00O00OO0000O0O00 ,OO0OO0O0O0OO0000O #line:913
    def _verifyact4ft (O0O0000OO0OOOO000 ,_O0OOOO0OOO0O00000 ):#line:915
        O0OO00OOO00OO00OO ={}#line:916
        for O0O00OO0OO00O0O00 in O0O0000OO0OOOO000 .task_actinfo ['cedents']:#line:917
            O0OO00OOO00OO00OO [O0O00OO0OO00O0O00 ['cedent_type']]=O0O00OO0OO00O0O00 ['filter_value']#line:919
        O00O00O000O0OOO0O =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv-']&O0OO00OOO00OO00OO ['sucv-'])#line:921
        OOO0O00OO0O00000O =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv+']&O0OO00OOO00OO00OO ['sucv+'])#line:922
        O0OO0O0O00O0OO00O =None #line:923
        OOOOOOO00O0O000OO =0 #line:924
        OOO00OO00O000O00O =0 #line:925
        if O00O00O000O0OOO0O >0 :#line:934
            OOOOOOO00O0O000OO =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv-']&O0OO00OOO00OO00OO ['sucv-'])*1.0 /O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv-'])#line:936
        if OOO0O00OO0O00000O >0 :#line:937
            OOO00OO00O000O00O =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv+']&O0OO00OOO00OO00OO ['sucv+'])*1.0 /O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv+'])#line:939
        O0O00O00OOO00O0OO =1 <<O0O0000OO0OOOO000 .data ["rows_count"]#line:941
        O00OO00OO0O0OO000 =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv-']&O0OO00OOO00OO00OO ['sucv-'])#line:942
        OOO000O000O0OOOOO =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['antv-']&~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['sucv-']))&O0OO00OOO00OO00OO ['cond'])#line:943
        OOOOO00O00O000OOO =O0O0000OO0OOOO000 ._bitcount (~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['antv-']))&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['sucv-'])#line:944
        OOOO00000O0000O00 =O0O0000OO0OOOO000 ._bitcount (~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['antv-']))&~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['sucv-']))&O0OO00OOO00OO00OO ['cond'])#line:945
        O000OOO00000OOOO0 =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['antv+']&O0OO00OOO00OO00OO ['sucv+'])#line:946
        O00O00O0O0O0000OO =O0O0000OO0OOOO000 ._bitcount (O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['antv+']&~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['sucv+']))&O0OO00OOO00OO00OO ['cond'])#line:947
        O0OO0O0OO0OOOOOO0 =O0O0000OO0OOOO000 ._bitcount (~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['antv+']))&O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['cond']&O0OO00OOO00OO00OO ['sucv+'])#line:948
        OO00OO000OOO0OO0O =O0O0000OO0OOOO000 ._bitcount (~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['ante']&O0OO00OOO00OO00OO ['antv+']))&~(O0O00O00OOO00O0OO |(O0OO00OOO00OO00OO ['succ']&O0OO00OOO00OO00OO ['sucv+']))&O0OO00OOO00OO00OO ['cond'])#line:949
        OOO0OOO00OO0OOO0O =True #line:950
        for OO0O00O00OOOO00OO in O0O0000OO0OOOO000 .quantifiers .keys ():#line:951
            if (OO0O00O00OOOO00OO =='PreBase')|(OO0O00O00OOOO00OO =='Base1'):#line:952
                OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=O00O00O000O0OOO0O )#line:953
            if (OO0O00O00OOOO00OO =='PostBase')|(OO0O00O00OOOO00OO =='Base2'):#line:954
                OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=OOO0O00OO0O00000O )#line:955
            if (OO0O00O00OOOO00OO =='PreRelBase')|(OO0O00O00OOOO00OO =='RelBase1'):#line:956
                OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=O00O00O000O0OOO0O *1.0 /O0O0000OO0OOOO000 .data ["rows_count"])#line:957
            if (OO0O00O00OOOO00OO =='PostRelBase')|(OO0O00O00OOOO00OO =='RelBase2'):#line:958
                OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=OOO0O00OO0O00000O *1.0 /O0O0000OO0OOOO000 .data ["rows_count"])#line:959
            if (OO0O00O00OOOO00OO =='Prepim')|(OO0O00O00OOOO00OO =='pim1')|(OO0O00O00OOOO00OO =='PreConf')|(OO0O00O00OOOO00OO =='conf1'):#line:960
                OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=OOOOOOO00O0O000OO )#line:961
            if (OO0O00O00OOOO00OO =='Postpim')|(OO0O00O00OOOO00OO =='pim2')|(OO0O00O00OOOO00OO =='PostConf')|(OO0O00O00OOOO00OO =='conf2'):#line:962
                OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=OOO00OO00O000O00O )#line:963
            if (OO0O00O00OOOO00OO =='Deltapim')|(OO0O00O00OOOO00OO =='DeltaConf'):#line:964
                OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=OOOOOOO00O0O000OO -OOO00OO00O000O00O )#line:965
            if (OO0O00O00OOOO00OO =='Ratiopim')|(OO0O00O00OOOO00OO =='RatioConf'):#line:968
                if (OOOOOOO00O0O000OO >0 ):#line:969
                    OOO0OOO00OO0OOO0O =OOO0OOO00OO0OOO0O and (O0O0000OO0OOOO000 .quantifiers .get (OO0O00O00OOOO00OO )<=OOO00OO00O000O00O *1.0 /OOOOOOO00O0O000OO )#line:970
                else :#line:971
                    OOO0OOO00OO0OOO0O =False #line:972
        O0O0000OO0O00OOO0 ={}#line:973
        if OOO0OOO00OO0OOO0O ==True :#line:974
            O0O0000OO0OOOO000 .stats ['total_valid']+=1 #line:976
            O0O0000OO0O00OOO0 ["base1"]=O00O00O000O0OOO0O #line:977
            O0O0000OO0O00OOO0 ["base2"]=OOO0O00OO0O00000O #line:978
            O0O0000OO0O00OOO0 ["rel_base1"]=O00O00O000O0OOO0O *1.0 /O0O0000OO0OOOO000 .data ["rows_count"]#line:979
            O0O0000OO0O00OOO0 ["rel_base2"]=OOO0O00OO0O00000O *1.0 /O0O0000OO0OOOO000 .data ["rows_count"]#line:980
            O0O0000OO0O00OOO0 ["conf1"]=OOOOOOO00O0O000OO #line:981
            O0O0000OO0O00OOO0 ["conf2"]=OOO00OO00O000O00O #line:982
            O0O0000OO0O00OOO0 ["deltaconf"]=OOOOOOO00O0O000OO -OOO00OO00O000O00O #line:983
            if (OOOOOOO00O0O000OO >0 ):#line:984
                O0O0000OO0O00OOO0 ["ratioconf"]=OOO00OO00O000O00O *1.0 /OOOOOOO00O0O000OO #line:985
            else :#line:986
                O0O0000OO0O00OOO0 ["ratioconf"]=None #line:987
            O0O0000OO0O00OOO0 ["fourfoldpre"]=[O00OO00OO0O0OO000 ,OOO000O000O0OOOOO ,OOOOO00O00O000OOO ,OOOO00000O0000O00 ]#line:988
            O0O0000OO0O00OOO0 ["fourfoldpost"]=[O000OOO00000OOOO0 ,O00O00O0O0O0000OO ,O0OO0O0OO0OOOOOO0 ,OO00OO000OOO0OO0O ]#line:989
        return OOO0OOO00OO0OOO0O ,O0O0000OO0O00OOO0 #line:991
    def _verify_opt (OO000OOO0000OOO00 ,OO00OOO000OO00000 ,O0OO00OOO0OOOO0OO ):#line:993
        OO000OOO0000OOO00 .stats ['total_ver']+=1 #line:994
        OOOO0O00OOOO0OO0O =False #line:995
        if not (OO00OOO000OO00000 ['optim'].get ('only_con')):#line:998
            return False #line:999
        if not (OO000OOO0000OOO00 .options ['optimizations']):#line:1002
            return False #line:1004
        OOO0O0OO0OO0O0O0O ={}#line:1006
        for OOO0O0O0OOO0OO0OO in OO000OOO0000OOO00 .task_actinfo ['cedents']:#line:1007
            OOO0O0OO0OO0O0O0O [OOO0O0O0OOO0OO0OO ['cedent_type']]=OOO0O0O0OOO0OO0OO ['filter_value']#line:1009
        O0OO0O00OOO00O00O =1 <<OO000OOO0000OOO00 .data ["rows_count"]#line:1011
        OO0OOOOOO0OOO0OOO =O0OO0O00OOO00O00O -1 #line:1012
        OO0OO0OOOOO0OOOO0 =""#line:1013
        O0OO00OOOO000O000 =0 #line:1014
        if (OOO0O0OO0OO0O0O0O .get ('ante')!=None ):#line:1015
            OO0OOOOOO0OOO0OOO =OO0OOOOOO0OOO0OOO &OOO0O0OO0OO0O0O0O ['ante']#line:1016
        if (OOO0O0OO0OO0O0O0O .get ('succ')!=None ):#line:1017
            OO0OOOOOO0OOO0OOO =OO0OOOOOO0OOO0OOO &OOO0O0OO0OO0O0O0O ['succ']#line:1018
        if (OOO0O0OO0OO0O0O0O .get ('cond')!=None ):#line:1019
            OO0OOOOOO0OOO0OOO =OO0OOOOOO0OOO0OOO &OOO0O0OO0OO0O0O0O ['cond']#line:1020
        OOO00OOOO000O0OOO =None #line:1023
        if (OO000OOO0000OOO00 .proc =='CFMiner')|(OO000OOO0000OOO00 .proc =='4ftMiner')|(OO000OOO0000OOO00 .proc =='UICMiner'):#line:1048
            OO0OO00OOOOO00OOO =OO000OOO0000OOO00 ._bitcount (OO0OOOOOO0OOO0OOO )#line:1049
            if not (OO000OOO0000OOO00 ._opt_base ==None ):#line:1050
                if not (OO000OOO0000OOO00 ._opt_base <=OO0OO00OOOOO00OOO ):#line:1051
                    OOOO0O00OOOO0OO0O =True #line:1052
            if not (OO000OOO0000OOO00 ._opt_relbase ==None ):#line:1054
                if not (OO000OOO0000OOO00 ._opt_relbase <=OO0OO00OOOOO00OOO *1.0 /OO000OOO0000OOO00 .data ["rows_count"]):#line:1055
                    OOOO0O00OOOO0OO0O =True #line:1056
        if (OO000OOO0000OOO00 .proc =='SD4ftMiner'):#line:1058
            OO0OO00OOOOO00OOO =OO000OOO0000OOO00 ._bitcount (OO0OOOOOO0OOO0OOO )#line:1059
            if (not (OO000OOO0000OOO00 ._opt_base1 ==None ))&(not (OO000OOO0000OOO00 ._opt_base2 ==None )):#line:1060
                if not (max (OO000OOO0000OOO00 ._opt_base1 ,OO000OOO0000OOO00 ._opt_base2 )<=OO0OO00OOOOO00OOO ):#line:1061
                    OOOO0O00OOOO0OO0O =True #line:1063
            if (not (OO000OOO0000OOO00 ._opt_relbase1 ==None ))&(not (OO000OOO0000OOO00 ._opt_relbase2 ==None )):#line:1064
                if not (max (OO000OOO0000OOO00 ._opt_relbase1 ,OO000OOO0000OOO00 ._opt_relbase2 )<=OO0OO00OOOOO00OOO *1.0 /OO000OOO0000OOO00 .data ["rows_count"]):#line:1065
                    OOOO0O00OOOO0OO0O =True #line:1066
        return OOOO0O00OOOO0OO0O #line:1068
        if OO000OOO0000OOO00 .proc =='CFMiner':#line:1071
            if (O0OO00OOO0OOOO0OO ['cedent_type']=='cond')&(O0OO00OOO0OOOO0OO ['defi'].get ('type')=='con'):#line:1072
                OO0OO00OOOOO00OOO =bin (OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1073
                O000OO0OO00000O00 =True #line:1074
                for O00O0OO000O0O0O00 in OO000OOO0000OOO00 .quantifiers .keys ():#line:1075
                    if O00O0OO000O0O0O00 =='Base':#line:1076
                        O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=OO0OO00OOOOO00OOO )#line:1077
                        if not (O000OO0OO00000O00 ):#line:1078
                            print (f"...optimization : base is {OO0OO00OOOOO00OOO} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1079
                    if O00O0OO000O0O0O00 =='RelBase':#line:1080
                        O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=OO0OO00OOOOO00OOO *1.0 /OO000OOO0000OOO00 .data ["rows_count"])#line:1081
                        if not (O000OO0OO00000O00 ):#line:1082
                            print (f"...optimization : base is {OO0OO00OOOOO00OOO} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1083
                OOOO0O00OOOO0OO0O =not (O000OO0OO00000O00 )#line:1084
        elif OO000OOO0000OOO00 .proc =='4ftMiner':#line:1085
            if (O0OO00OOO0OOOO0OO ['cedent_type']=='cond')&(O0OO00OOO0OOOO0OO ['defi'].get ('type')=='con'):#line:1086
                OO0OO00OOOOO00OOO =bin (OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1087
                O000OO0OO00000O00 =True #line:1088
                for O00O0OO000O0O0O00 in OO000OOO0000OOO00 .quantifiers .keys ():#line:1089
                    if O00O0OO000O0O0O00 =='Base':#line:1090
                        O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=OO0OO00OOOOO00OOO )#line:1091
                        if not (O000OO0OO00000O00 ):#line:1092
                            print (f"...optimization : base is {OO0OO00OOOOO00OOO} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1093
                    if O00O0OO000O0O0O00 =='RelBase':#line:1094
                        O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=OO0OO00OOOOO00OOO *1.0 /OO000OOO0000OOO00 .data ["rows_count"])#line:1095
                        if not (O000OO0OO00000O00 ):#line:1096
                            print (f"...optimization : base is {OO0OO00OOOOO00OOO} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1097
                OOOO0O00OOOO0OO0O =not (O000OO0OO00000O00 )#line:1098
            if (O0OO00OOO0OOOO0OO ['cedent_type']=='ante')&(O0OO00OOO0OOOO0OO ['defi'].get ('type')=='con'):#line:1099
                OO0OO00OOOOO00OOO =bin (OOO0O0OO0OO0O0O0O ['ante']&OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1100
                O000OO0OO00000O00 =True #line:1101
                for O00O0OO000O0O0O00 in OO000OOO0000OOO00 .quantifiers .keys ():#line:1102
                    if O00O0OO000O0O0O00 =='Base':#line:1103
                        O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=OO0OO00OOOOO00OOO )#line:1104
                        if not (O000OO0OO00000O00 ):#line:1105
                            print (f"...optimization : ANTE: base is {OO0OO00OOOOO00OOO} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1106
                    if O00O0OO000O0O0O00 =='RelBase':#line:1107
                        O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=OO0OO00OOOOO00OOO *1.0 /OO000OOO0000OOO00 .data ["rows_count"])#line:1108
                        if not (O000OO0OO00000O00 ):#line:1109
                            print (f"...optimization : ANTE:  base is {OO0OO00OOOOO00OOO} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1110
                OOOO0O00OOOO0OO0O =not (O000OO0OO00000O00 )#line:1111
            if (O0OO00OOO0OOOO0OO ['cedent_type']=='succ')&(O0OO00OOO0OOOO0OO ['defi'].get ('type')=='con'):#line:1112
                OO0OO00OOOOO00OOO =bin (OOO0O0OO0OO0O0O0O ['ante']&OOO0O0OO0OO0O0O0O ['cond']&OOO0O0OO0OO0O0O0O ['succ']).count ("1")#line:1113
                OOO00OOOO000O0OOO =0 #line:1114
                if OO0OO00OOOOO00OOO >0 :#line:1115
                    OOO00OOOO000O0OOO =bin (OOO0O0OO0OO0O0O0O ['ante']&OOO0O0OO0OO0O0O0O ['succ']&OOO0O0OO0OO0O0O0O ['cond']).count ("1")*1.0 /bin (OOO0O0OO0OO0O0O0O ['ante']&OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1116
                O0OO0O00OOO00O00O =1 <<OO000OOO0000OOO00 .data ["rows_count"]#line:1117
                O00000OO0O00O00O0 =bin (OOO0O0OO0OO0O0O0O ['ante']&OOO0O0OO0OO0O0O0O ['succ']&OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1118
                O00OO0OOO00O00O00 =bin (OOO0O0OO0OO0O0O0O ['ante']&~(O0OO0O00OOO00O00O |OOO0O0OO0OO0O0O0O ['succ'])&OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1119
                OOO0O0O0OOO0OO0OO =bin (~(O0OO0O00OOO00O00O |OOO0O0OO0OO0O0O0O ['ante'])&OOO0O0OO0OO0O0O0O ['succ']&OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1120
                O0O0OOO0000OO0O00 =bin (~(O0OO0O00OOO00O00O |OOO0O0OO0OO0O0O0O ['ante'])&~(O0OO0O00OOO00O00O |OOO0O0OO0OO0O0O0O ['succ'])&OOO0O0OO0OO0O0O0O ['cond']).count ("1")#line:1121
                O000OO0OO00000O00 =True #line:1122
                for O00O0OO000O0O0O00 in OO000OOO0000OOO00 .quantifiers .keys ():#line:1123
                    if O00O0OO000O0O0O00 =='pim':#line:1124
                        O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=OOO00OOOO000O0OOO )#line:1125
                    if not (O000OO0OO00000O00 ):#line:1126
                        print (f"...optimization : SUCC:  pim is {OOO00OOOO000O0OOO} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1127
                    if O00O0OO000O0O0O00 =='aad':#line:1129
                        if (O00000OO0O00O00O0 +O00OO0OOO00O00O00 )*(O00000OO0O00O00O0 +OOO0O0O0OOO0OO0OO )>0 :#line:1130
                            O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=O00000OO0O00O00O0 *(O00000OO0O00O00O0 +O00OO0OOO00O00O00 +OOO0O0O0OOO0OO0OO +O0O0OOO0000OO0O00 )/(O00000OO0O00O00O0 +O00OO0OOO00O00O00 )/(O00000OO0O00O00O0 +OOO0O0O0OOO0OO0OO )-1 )#line:1131
                        else :#line:1132
                            O000OO0OO00000O00 =False #line:1133
                        if not (O000OO0OO00000O00 ):#line:1134
                            O0OO0O0OOO00O0000 =O00000OO0O00O00O0 *(O00000OO0O00O00O0 +O00OO0OOO00O00O00 +OOO0O0O0OOO0OO0OO +O0O0OOO0000OO0O00 )/(O00000OO0O00O00O0 +O00OO0OOO00O00O00 )/(O00000OO0O00O00O0 +OOO0O0O0OOO0OO0OO )-1 #line:1135
                            print (f"...optimization : SUCC:  aad is {O0OO0O0OOO00O0000} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1136
                    if O00O0OO000O0O0O00 =='bad':#line:1137
                        if (O00000OO0O00O00O0 +O00OO0OOO00O00O00 )*(O00000OO0O00O00O0 +OOO0O0O0OOO0OO0OO )>0 :#line:1138
                            O000OO0OO00000O00 =O000OO0OO00000O00 and (OO000OOO0000OOO00 .quantifiers .get (O00O0OO000O0O0O00 )<=1 -O00000OO0O00O00O0 *(O00000OO0O00O00O0 +O00OO0OOO00O00O00 +OOO0O0O0OOO0OO0OO +O0O0OOO0000OO0O00 )/(O00000OO0O00O00O0 +O00OO0OOO00O00O00 )/(O00000OO0O00O00O0 +OOO0O0O0OOO0OO0OO ))#line:1139
                        else :#line:1140
                            O000OO0OO00000O00 =False #line:1141
                        if not (O000OO0OO00000O00 ):#line:1142
                            OOOOO0O0O0OOOOO00 =1 -O00000OO0O00O00O0 *(O00000OO0O00O00O0 +O00OO0OOO00O00O00 +OOO0O0O0OOO0OO0OO +O0O0OOO0000OO0O00 )/(O00000OO0O00O00O0 +O00OO0OOO00O00O00 )/(O00000OO0O00O00O0 +OOO0O0O0OOO0OO0OO )#line:1143
                            print (f"...optimization : SUCC:  bad is {OOOOO0O0O0OOOOO00} for {O0OO00OOO0OOOO0OO['generated_string']}")#line:1144
                OOOO0O00OOOO0OO0O =not (O000OO0OO00000O00 )#line:1145
        if (OOOO0O00OOOO0OO0O ):#line:1146
            print (f"... OPTIMALIZATION - SKIPPING BRANCH at cedent {O0OO00OOO0OOOO0OO['cedent_type']}")#line:1147
        return OOOO0O00OOOO0OO0O #line:1148
    def _print (O0O00OOO000000O00 ,O0O00OO00O00O0000 ,_O0OOO00OO00OOOO0O ,_O00O00O00OOO00O00 ):#line:1151
        if (len (_O0OOO00OO00OOOO0O ))!=len (_O00O00O00OOO00O00 ):#line:1152
            print ("DIFF IN LEN for following cedent : "+str (len (_O0OOO00OO00OOOO0O ))+" vs "+str (len (_O00O00O00OOO00O00 )))#line:1153
            print ("trace cedent : "+str (_O0OOO00OO00OOOO0O )+", traces "+str (_O00O00O00OOO00O00 ))#line:1154
        O00O00000O0000O00 =''#line:1155
        O0000OOO0OOOO0000 ={}#line:1156
        OO0000O000000O000 =[]#line:1157
        for O00OO0O000O0OOO00 in range (len (_O0OOO00OO00OOOO0O )):#line:1158
            OO00O0OO0O000OO00 =O0O00OOO000000O00 .data ["varname"].index (O0O00OO00O00O0000 ['defi'].get ('attributes')[_O0OOO00OO00OOOO0O [O00OO0O000O0OOO00 ]].get ('name'))#line:1159
            O00O00000O0000O00 =O00O00000O0000O00 +O0O00OOO000000O00 .data ["varname"][OO00O0OO0O000OO00 ]+'('#line:1161
            OO0000O000000O000 .append (OO00O0OO0O000OO00 )#line:1162
            OOO000000OOOOOO0O =[]#line:1163
            for OOO0O00000O0O0000 in _O00O00O00OOO00O00 [O00OO0O000O0OOO00 ]:#line:1164
                O00O00000O0000O00 =O00O00000O0000O00 +str (O0O00OOO000000O00 .data ["catnames"][OO00O0OO0O000OO00 ][OOO0O00000O0O0000 ])+" "#line:1165
                OOO000000OOOOOO0O .append (str (O0O00OOO000000O00 .data ["catnames"][OO00O0OO0O000OO00 ][OOO0O00000O0O0000 ]))#line:1166
            O00O00000O0000O00 =O00O00000O0000O00 [:-1 ]+')'#line:1167
            O0000OOO0OOOO0000 [O0O00OOO000000O00 .data ["varname"][OO00O0OO0O000OO00 ]]=OOO000000OOOOOO0O #line:1168
            if O00OO0O000O0OOO00 +1 <len (_O0OOO00OO00OOOO0O ):#line:1169
                O00O00000O0000O00 =O00O00000O0000O00 +' & '#line:1170
        return O00O00000O0000O00 ,O0000OOO0OOOO0000 ,OO0000O000000O000 #line:1174
    def _print_hypo (O000O0O00OOO00OO0 ,O0O0O000OOOO0O00O ):#line:1176
        O000O0O00OOO00OO0 .print_rule (O0O0O000OOOO0O00O )#line:1177
    def _print_rule (O000OO00OO000O000 ,O0OO000O0OO0OOO0O ):#line:1179
        if O000OO00OO000O000 .verbosity ['print_rules']:#line:1180
            print ('Rules info : '+str (O0OO000O0OO0OOO0O ['params']))#line:1181
            for OO0O00OOOO0O00000 in O000OO00OO000O000 .task_actinfo ['cedents']:#line:1182
                print (OO0O00OOOO0O00000 ['cedent_type']+' = '+OO0O00OOOO0O00000 ['generated_string'])#line:1183
    def _genvar (OO00O00000OOOOO00 ,OO00O0OO0O000O0OO ,O0OOO00O0O0O00O0O ,_OO000O0O00OO00OOO ,_O000OOOO000000OOO ,_O0O0O0O000O0OOO00 ,_O0000OOO0000OOOOO ,_OO0O0O0O0OO00000O ,_O00O00OO0OOOOO0OO ,_O0O0OO00OOO0O0OOO ):#line:1185
        _OOOO0O0O0OOOO0O0O =0 #line:1186
        if O0OOO00O0O0O00O0O ['num_cedent']>0 :#line:1187
            _OOOO0O0O0OOOO0O0O =(_O0O0OO00OOO0O0OOO -_O00O00OO0OOOOO0OO )/O0OOO00O0O0O00O0O ['num_cedent']#line:1188
        for OOO0OO0000O0OOOOO in range (O0OOO00O0O0O00O0O ['num_cedent']):#line:1189
            if len (_OO000O0O00OO00OOO )==0 or OOO0OO0000O0OOOOO >_OO000O0O00OO00OOO [-1 ]:#line:1190
                _OO000O0O00OO00OOO .append (OOO0OO0000O0OOOOO )#line:1191
                O0OOO0OO00OOOOO00 =OO00O00000OOOOO00 .data ["varname"].index (O0OOO00O0O0O00O0O ['defi'].get ('attributes')[OOO0OO0000O0OOOOO ].get ('name'))#line:1192
                _O000OOO00O000O000 =O0OOO00O0O0O00O0O ['defi'].get ('attributes')[OOO0OO0000O0OOOOO ].get ('minlen')#line:1193
                _OO00O0OO00O0O0OOO =O0OOO00O0O0O00O0O ['defi'].get ('attributes')[OOO0OO0000O0OOOOO ].get ('maxlen')#line:1194
                _O0O0OOOOOOO00O00O =O0OOO00O0O0O00O0O ['defi'].get ('attributes')[OOO0OO0000O0OOOOO ].get ('type')#line:1195
                OOO00000000000OOO =len (OO00O00000OOOOO00 .data ["dm"][O0OOO0OO00OOOOO00 ])#line:1196
                _OO00000OO00OO0000 =[]#line:1197
                _O000OOOO000000OOO .append (_OO00000OO00OO0000 )#line:1198
                _OOO0OOO00O0O000O0 =int (0 )#line:1199
                OO00O00000OOOOO00 ._gencomb (OO00O0OO0O000O0OO ,O0OOO00O0O0O00O0O ,_OO000O0O00OO00OOO ,_O000OOOO000000OOO ,_OO00000OO00OO0000 ,_O0O0O0O000O0OOO00 ,_OOO0OOO00O0O000O0 ,OOO00000000000OOO ,_O0O0OOOOOOO00O00O ,_O0000OOO0000OOOOO ,_OO0O0O0O0OO00000O ,_O000OOO00O000O000 ,_OO00O0OO00O0O0OOO ,_O00O00OO0OOOOO0OO +OOO0OO0000O0OOOOO *_OOOO0O0O0OOOO0O0O ,_O00O00OO0OOOOO0OO +(OOO0OO0000O0OOOOO +1 )*_OOOO0O0O0OOOO0O0O )#line:1200
                _O000OOOO000000OOO .pop ()#line:1201
                _OO000O0O00OO00OOO .pop ()#line:1202
    def _gencomb (OOOOO000OO0O0OOO0 ,O0OOOOOOOO00O0000 ,O0OO0OO0O00OOOO0O ,_OOOOOO0OOOOO0OO00 ,_OO0O0O0O000OOO0O0 ,_OOOO0O0O0000OOO00 ,_O00000OO00O0O000O ,_O000000OOOO0OOO00 ,O00O00O0O0O0O0OO0 ,_OOOOOOO00O00O00OO ,_O0O000OO0O0OO0000 ,_O0OOOO0O0000O00O0 ,_OO0OOO0OOOOO0OOO0 ,_O00O00OO000000O00 ,_O0O00O0000O00000O ,_O0O00O00OOOO00000 ):#line:1204
        _OOO0OO00000OOOOO0 =[]#line:1205
        if _OOOOOOO00O00O00OO =="subset":#line:1206
            if len (_OOOO0O0O0000OOO00 )==0 :#line:1207
                _OOO0OO00000OOOOO0 =range (O00O00O0O0O0O0OO0 )#line:1208
            else :#line:1209
                _OOO0OO00000OOOOO0 =range (_OOOO0O0O0000OOO00 [-1 ]+1 ,O00O00O0O0O0O0OO0 )#line:1210
        elif _OOOOOOO00O00O00OO =="seq":#line:1211
            if len (_OOOO0O0O0000OOO00 )==0 :#line:1212
                _OOO0OO00000OOOOO0 =range (O00O00O0O0O0O0OO0 -_OO0OOO0OOOOO0OOO0 +1 )#line:1213
            else :#line:1214
                if _OOOO0O0O0000OOO00 [-1 ]+1 ==O00O00O0O0O0O0OO0 :#line:1215
                    return #line:1216
                OO00000000O00O000 =_OOOO0O0O0000OOO00 [-1 ]+1 #line:1217
                _OOO0OO00000OOOOO0 .append (OO00000000O00O000 )#line:1218
        elif _OOOOOOO00O00O00OO =="lcut":#line:1219
            if len (_OOOO0O0O0000OOO00 )==0 :#line:1220
                OO00000000O00O000 =0 ;#line:1221
            else :#line:1222
                if _OOOO0O0O0000OOO00 [-1 ]+1 ==O00O00O0O0O0O0OO0 :#line:1223
                    return #line:1224
                OO00000000O00O000 =_OOOO0O0O0000OOO00 [-1 ]+1 #line:1225
            _OOO0OO00000OOOOO0 .append (OO00000000O00O000 )#line:1226
        elif _OOOOOOO00O00O00OO =="rcut":#line:1227
            if len (_OOOO0O0O0000OOO00 )==0 :#line:1228
                OO00000000O00O000 =O00O00O0O0O0O0OO0 -1 ;#line:1229
            else :#line:1230
                if _OOOO0O0O0000OOO00 [-1 ]==0 :#line:1231
                    return #line:1232
                OO00000000O00O000 =_OOOO0O0O0000OOO00 [-1 ]-1 #line:1233
            _OOO0OO00000OOOOO0 .append (OO00000000O00O000 )#line:1235
        elif _OOOOOOO00O00O00OO =="one":#line:1236
            if len (_OOOO0O0O0000OOO00 )==0 :#line:1237
                OO00000000OOO0O0O =OOOOO000OO0O0OOO0 .data ["varname"].index (O0OO0OO0O00OOOO0O ['defi'].get ('attributes')[_OOOOOO0OOOOO0OO00 [-1 ]].get ('name'))#line:1238
                try :#line:1239
                    OO00000000O00O000 =OOOOO000OO0O0OOO0 .data ["catnames"][OO00000000OOO0O0O ].index (O0OO0OO0O00OOOO0O ['defi'].get ('attributes')[_OOOOOO0OOOOO0OO00 [-1 ]].get ('value'))#line:1240
                except :#line:1241
                    print (f"ERROR: attribute '{O0OO0OO0O00OOOO0O['defi'].get('attributes')[_OOOOOO0OOOOO0OO00[-1]].get('name')}' has not value '{O0OO0OO0O00OOOO0O['defi'].get('attributes')[_OOOOOO0OOOOO0OO00[-1]].get('value')}'")#line:1242
                    exit (1 )#line:1243
                _OOO0OO00000OOOOO0 .append (OO00000000O00O000 )#line:1244
                _OO0OOO0OOOOO0OOO0 =1 #line:1245
                _O00O00OO000000O00 =1 #line:1246
            else :#line:1247
                print ("DEBUG: one category should not have more categories")#line:1248
                return #line:1249
        else :#line:1250
            print ("Attribute type "+_OOOOOOO00O00O00OO +" not supported.")#line:1251
            return #line:1252
        if len (_OOO0OO00000OOOOO0 )>0 :#line:1254
            _OO000OO0O00O000OO =(_O0O00O00OOOO00000 -_O0O00O0000O00000O )/len (_OOO0OO00000OOOOO0 )#line:1255
        else :#line:1256
            _OO000OO0O00O000OO =0 #line:1257
        _O000O0OO000O0OO0O =0 #line:1259
        for OO000OOO00O0000O0 in _OOO0OO00000OOOOO0 :#line:1261
                _OOOO0O0O0000OOO00 .append (OO000OOO00O0000O0 )#line:1263
                _OO0O0O0O000OOO0O0 .pop ()#line:1264
                _OO0O0O0O000OOO0O0 .append (_OOOO0O0O0000OOO00 )#line:1265
                _OOO0O0000O0OOO0O0 =_O000000OOOO0OOO00 |OOOOO000OO0O0OOO0 .data ["dm"][OOOOO000OO0O0OOO0 .data ["varname"].index (O0OO0OO0O00OOOO0O ['defi'].get ('attributes')[_OOOOOO0OOOOO0OO00 [-1 ]].get ('name'))][OO000OOO00O0000O0 ]#line:1269
                _O0O0OOO0OO000OO00 =1 #line:1271
                if (len (_OOOOOO0OOOOO0OO00 )<_O0O000OO0O0OO0000 ):#line:1272
                    _O0O0OOO0OO000OO00 =-1 #line:1273
                if (len (_OO0O0O0O000OOO0O0 [-1 ])<_OO0OOO0OOOOO0OOO0 ):#line:1275
                    _O0O0OOO0OO000OO00 =0 #line:1276
                _OO0O0OO00O00OO00O =0 #line:1278
                if O0OO0OO0O00OOOO0O ['defi'].get ('type')=='con':#line:1279
                    _OO0O0OO00O00OO00O =_O00000OO00O0O000O &_OOO0O0000O0OOO0O0 #line:1280
                else :#line:1281
                    _OO0O0OO00O00OO00O =_O00000OO00O0O000O |_OOO0O0000O0OOO0O0 #line:1282
                O0OO0OO0O00OOOO0O ['trace_cedent']=_OOOOOO0OOOOO0OO00 #line:1283
                O0OO0OO0O00OOOO0O ['traces']=_OO0O0O0O000OOO0O0 #line:1284
                O0000OOO0O000OOOO ,O0OO00OOO0OO000OO ,O0O000O0O0OO0O000 =OOOOO000OO0O0OOO0 ._print (O0OO0OO0O00OOOO0O ,_OOOOOO0OOOOO0OO00 ,_OO0O0O0O000OOO0O0 )#line:1285
                O0OO0OO0O00OOOO0O ['generated_string']=O0000OOO0O000OOOO #line:1286
                O0OO0OO0O00OOOO0O ['rule']=O0OO00OOO0OO000OO #line:1287
                O0OO0OO0O00OOOO0O ['filter_value']=_OO0O0OO00O00OO00O #line:1288
                O0OO0OO0O00OOOO0O ['traces']=copy .deepcopy (_OO0O0O0O000OOO0O0 )#line:1289
                O0OO0OO0O00OOOO0O ['trace_cedent']=copy .deepcopy (_OOOOOO0OOOOO0OO00 )#line:1290
                O0OO0OO0O00OOOO0O ['trace_cedent_asindata']=copy .deepcopy (O0O000O0O0OO0O000 )#line:1291
                O0OOOOOOOO00O0000 ['cedents'].append (O0OO0OO0O00OOOO0O )#line:1293
                O0OOO0OOOO000O00O =OOOOO000OO0O0OOO0 ._verify_opt (O0OOOOOOOO00O0000 ,O0OO0OO0O00OOOO0O )#line:1294
                if not (O0OOO0OOOO000O00O ):#line:1300
                    if _O0O0OOO0OO000OO00 ==1 :#line:1301
                        if len (O0OOOOOOOO00O0000 ['cedents_to_do'])==len (O0OOOOOOOO00O0000 ['cedents']):#line:1303
                            if OOOOO000OO0O0OOO0 .proc =='CFMiner':#line:1304
                                O0O0OOOOO000O00O0 ,OOOOOO00000OO00O0 =OOOOO000OO0O0OOO0 ._verifyCF (_OO0O0OO00O00OO00O )#line:1305
                            elif OOOOO000OO0O0OOO0 .proc =='UICMiner':#line:1306
                                O0O0OOOOO000O00O0 ,OOOOOO00000OO00O0 =OOOOO000OO0O0OOO0 ._verifyUIC (_OO0O0OO00O00OO00O )#line:1307
                            elif OOOOO000OO0O0OOO0 .proc =='4ftMiner':#line:1308
                                O0O0OOOOO000O00O0 ,OOOOOO00000OO00O0 =OOOOO000OO0O0OOO0 ._verify4ft (_OOO0O0000O0OOO0O0 )#line:1309
                            elif OOOOO000OO0O0OOO0 .proc =='SD4ftMiner':#line:1310
                                O0O0OOOOO000O00O0 ,OOOOOO00000OO00O0 =OOOOO000OO0O0OOO0 ._verifysd4ft (_OOO0O0000O0OOO0O0 )#line:1311
                            elif OOOOO000OO0O0OOO0 .proc =='NewAct4ftMiner':#line:1312
                                O0O0OOOOO000O00O0 ,OOOOOO00000OO00O0 =OOOOO000OO0O0OOO0 ._verifynewact4ft (_OOO0O0000O0OOO0O0 )#line:1313
                            elif OOOOO000OO0O0OOO0 .proc =='Act4ftMiner':#line:1314
                                O0O0OOOOO000O00O0 ,OOOOOO00000OO00O0 =OOOOO000OO0O0OOO0 ._verifyact4ft (_OOO0O0000O0OOO0O0 )#line:1315
                            else :#line:1316
                                print ("Unsupported procedure : "+OOOOO000OO0O0OOO0 .proc )#line:1317
                                exit (0 )#line:1318
                            if O0O0OOOOO000O00O0 ==True :#line:1319
                                OO0OOO00O0O00O0O0 ={}#line:1320
                                OO0OOO00O0O00O0O0 ["rule_id"]=OOOOO000OO0O0OOO0 .stats ['total_valid']#line:1321
                                OO0OOO00O0O00O0O0 ["cedents_str"]={}#line:1322
                                OO0OOO00O0O00O0O0 ["cedents_struct"]={}#line:1323
                                OO0OOO00O0O00O0O0 ['traces']={}#line:1324
                                OO0OOO00O0O00O0O0 ['trace_cedent_taskorder']={}#line:1325
                                OO0OOO00O0O00O0O0 ['trace_cedent_dataorder']={}#line:1326
                                for O0OOOOOO00O00000O in O0OOOOOOOO00O0000 ['cedents']:#line:1327
                                    OO0OOO00O0O00O0O0 ['cedents_str'][O0OOOOOO00O00000O ['cedent_type']]=O0OOOOOO00O00000O ['generated_string']#line:1329
                                    OO0OOO00O0O00O0O0 ['cedents_struct'][O0OOOOOO00O00000O ['cedent_type']]=O0OOOOOO00O00000O ['rule']#line:1330
                                    OO0OOO00O0O00O0O0 ['traces'][O0OOOOOO00O00000O ['cedent_type']]=O0OOOOOO00O00000O ['traces']#line:1331
                                    OO0OOO00O0O00O0O0 ['trace_cedent_taskorder'][O0OOOOOO00O00000O ['cedent_type']]=O0OOOOOO00O00000O ['trace_cedent']#line:1332
                                    OO0OOO00O0O00O0O0 ['trace_cedent_dataorder'][O0OOOOOO00O00000O ['cedent_type']]=O0OOOOOO00O00000O ['trace_cedent_asindata']#line:1333
                                OO0OOO00O0O00O0O0 ["params"]=OOOOOO00000OO00O0 #line:1335
                                OOOOO000OO0O0OOO0 ._print_rule (OO0OOO00O0O00O0O0 )#line:1337
                                OOOOO000OO0O0OOO0 .rulelist .append (OO0OOO00O0O00O0O0 )#line:1343
                            OOOOO000OO0O0OOO0 .stats ['total_cnt']+=1 #line:1345
                            OOOOO000OO0O0OOO0 .stats ['total_ver']+=1 #line:1346
                    if _O0O0OOO0OO000OO00 >=0 :#line:1347
                        if len (O0OOOOOOOO00O0000 ['cedents_to_do'])>len (O0OOOOOOOO00O0000 ['cedents']):#line:1348
                            OOOOO000OO0O0OOO0 ._start_cedent (O0OOOOOOOO00O0000 ,_O0O00O0000O00000O +_O000O0OO000O0OO0O *_OO000OO0O00O000OO ,_O0O00O0000O00000O +(_O000O0OO000O0OO0O +0.33 )*_OO000OO0O00O000OO )#line:1349
                    O0OOOOOOOO00O0000 ['cedents'].pop ()#line:1350
                    if (len (_OOOOOO0OOOOO0OO00 )<_O0OOOO0O0000O00O0 ):#line:1351
                        OOOOO000OO0O0OOO0 ._genvar (O0OOOOOOOO00O0000 ,O0OO0OO0O00OOOO0O ,_OOOOOO0OOOOO0OO00 ,_OO0O0O0O000OOO0O0 ,_OO0O0OO00O00OO00O ,_O0O000OO0O0OO0000 ,_O0OOOO0O0000O00O0 ,_O0O00O0000O00000O +(_O000O0OO000O0OO0O +0.33 )*_OO000OO0O00O000OO ,_O0O00O0000O00000O +(_O000O0OO000O0OO0O +0.66 )*_OO000OO0O00O000OO )#line:1352
                else :#line:1353
                    O0OOOOOOOO00O0000 ['cedents'].pop ()#line:1354
                if len (_OOOO0O0O0000OOO00 )<_O00O00OO000000O00 :#line:1355
                    OOOOO000OO0O0OOO0 ._gencomb (O0OOOOOOOO00O0000 ,O0OO0OO0O00OOOO0O ,_OOOOOO0OOOOO0OO00 ,_OO0O0O0O000OOO0O0 ,_OOOO0O0O0000OOO00 ,_O00000OO00O0O000O ,_OOO0O0000O0OOO0O0 ,O00O00O0O0O0O0OO0 ,_OOOOOOO00O00O00OO ,_O0O000OO0O0OO0000 ,_O0OOOO0O0000O00O0 ,_OO0OOO0OOOOO0OOO0 ,_O00O00OO000000O00 ,_O0O00O0000O00000O +_OO000OO0O00O000OO *(_O000O0OO000O0OO0O +0.66 ),_O0O00O0000O00000O +_OO000OO0O00O000OO *(_O000O0OO000O0OO0O +1 ))#line:1356
                _OOOO0O0O0000OOO00 .pop ()#line:1357
                _O000O0OO000O0OO0O +=1 #line:1358
                if OOOOO000OO0O0OOO0 .options ['progressbar']:#line:1359
                    OOOOO000OO0O0OOO0 .bar .update (min (100 ,_O0O00O0000O00000O +_OO000OO0O00O000OO *_O000O0OO000O0OO0O ))#line:1360
    def _start_cedent (OO00O0O00OO000O0O ,O00000OOO000O00OO ,_O0OOOO0000000OO00 ,_O0OOO00OOO0O0OOOO ):#line:1363
        if len (O00000OOO000O00OO ['cedents_to_do'])>len (O00000OOO000O00OO ['cedents']):#line:1364
            _OOOO00O00O000O0O0 =[]#line:1365
            _O0000OO00O00OO0O0 =[]#line:1366
            OOO00000O00O0OOO0 ={}#line:1367
            OOO00000O00O0OOO0 ['cedent_type']=O00000OOO000O00OO ['cedents_to_do'][len (O00000OOO000O00OO ['cedents'])]#line:1368
            OOO000O00OO0OO00O =OOO00000O00O0OOO0 ['cedent_type']#line:1369
            if ((OOO000O00OO0OO00O [-1 ]=='-')|(OOO000O00OO0OO00O [-1 ]=='+')):#line:1370
                OOO000O00OO0OO00O =OOO000O00OO0OO00O [:-1 ]#line:1371
            OOO00000O00O0OOO0 ['defi']=OO00O0O00OO000O0O .kwargs .get (OOO000O00OO0OO00O )#line:1373
            if (OOO00000O00O0OOO0 ['defi']==None ):#line:1374
                print ("Error getting cedent ",OOO00000O00O0OOO0 ['cedent_type'])#line:1375
            _O000000OOOOOO0OOO =int (0 )#line:1376
            OOO00000O00O0OOO0 ['num_cedent']=len (OOO00000O00O0OOO0 ['defi'].get ('attributes'))#line:1383
            if (OOO00000O00O0OOO0 ['defi'].get ('type')=='con'):#line:1384
                _O000000OOOOOO0OOO =(1 <<OO00O0O00OO000O0O .data ["rows_count"])-1 #line:1385
            OO00O0O00OO000O0O ._genvar (O00000OOO000O00OO ,OOO00000O00O0OOO0 ,_OOOO00O00O000O0O0 ,_O0000OO00O00OO0O0 ,_O000000OOOOOO0OOO ,OOO00000O00O0OOO0 ['defi'].get ('minlen'),OOO00000O00O0OOO0 ['defi'].get ('maxlen'),_O0OOOO0000000OO00 ,_O0OOO00OOO0O0OOOO )#line:1386
    def _calc_all (OOO0O00O0OOO000OO ,**OOO0OO0OO00O00O00 ):#line:1389
        if "df"in OOO0OO0OO00O00O00 :#line:1390
            OOO0O00O0OOO000OO ._prep_data (OOO0O00O0OOO000OO .kwargs .get ("df"))#line:1391
        if not (OOO0O00O0OOO000OO ._initialized ):#line:1392
            print ("ERROR: dataframe is missing and not initialized with dataframe")#line:1393
        else :#line:1394
            OOO0O00O0OOO000OO ._calculate (**OOO0OO0OO00O00O00 )#line:1395
    def _check_cedents (O00O0OOOO0OOO00O0 ,O0000O0000OO0O000 ,**O00O00000O00OO000 ):#line:1397
        O000O000OO0O0O0O0 =True #line:1398
        if (O00O00000O00OO000 .get ('quantifiers',None )==None ):#line:1399
            print (f"Error: missing quantifiers.")#line:1400
            O000O000OO0O0O0O0 =False #line:1401
            return O000O000OO0O0O0O0 #line:1402
        if (type (O00O00000O00OO000 .get ('quantifiers'))!=dict ):#line:1403
            print (f"Error: quantifiers are not dictionary type.")#line:1404
            O000O000OO0O0O0O0 =False #line:1405
            return O000O000OO0O0O0O0 #line:1406
        for O00OO0OOO0OO000OO in O0000O0000OO0O000 :#line:1408
            if (O00O00000O00OO000 .get (O00OO0OOO0OO000OO ,None )==None ):#line:1409
                print (f"Error: cedent {O00OO0OOO0OO000OO} is missing in parameters.")#line:1410
                O000O000OO0O0O0O0 =False #line:1411
                return O000O000OO0O0O0O0 #line:1412
            O0OO00OO0OO00O0O0 =O00O00000O00OO000 .get (O00OO0OOO0OO000OO )#line:1413
            if (O0OO00OO0OO00O0O0 .get ('minlen'),None )==None :#line:1414
                print (f"Error: cedent {O00OO0OOO0OO000OO} has no minimal length specified.")#line:1415
                O000O000OO0O0O0O0 =False #line:1416
                return O000O000OO0O0O0O0 #line:1417
            if not (type (O0OO00OO0OO00O0O0 .get ('minlen'))is int ):#line:1418
                print (f"Error: cedent {O00OO0OOO0OO000OO} has invalid type of minimal length ({type(O0OO00OO0OO00O0O0.get('minlen'))}).")#line:1419
                O000O000OO0O0O0O0 =False #line:1420
                return O000O000OO0O0O0O0 #line:1421
            if (O0OO00OO0OO00O0O0 .get ('maxlen'),None )==None :#line:1422
                print (f"Error: cedent {O00OO0OOO0OO000OO} has no maximal length specified.")#line:1423
                O000O000OO0O0O0O0 =False #line:1424
                return O000O000OO0O0O0O0 #line:1425
            if not (type (O0OO00OO0OO00O0O0 .get ('maxlen'))is int ):#line:1426
                print (f"Error: cedent {O00OO0OOO0OO000OO} has invalid type of maximal length.")#line:1427
                O000O000OO0O0O0O0 =False #line:1428
                return O000O000OO0O0O0O0 #line:1429
            if (O0OO00OO0OO00O0O0 .get ('type'),None )==None :#line:1430
                print (f"Error: cedent {O00OO0OOO0OO000OO} has no type specified.")#line:1431
                O000O000OO0O0O0O0 =False #line:1432
                return O000O000OO0O0O0O0 #line:1433
            if not ((O0OO00OO0OO00O0O0 .get ('type'))in (['con','dis'])):#line:1434
                print (f"Error: cedent {O00OO0OOO0OO000OO} has invalid type. Allowed values are 'con' and 'dis'.")#line:1435
                O000O000OO0O0O0O0 =False #line:1436
                return O000O000OO0O0O0O0 #line:1437
            if (O0OO00OO0OO00O0O0 .get ('attributes'),None )==None :#line:1438
                print (f"Error: cedent {O00OO0OOO0OO000OO} has no attributes specified.")#line:1439
                O000O000OO0O0O0O0 =False #line:1440
                return O000O000OO0O0O0O0 #line:1441
            for OO0O00O0000O00O0O in O0OO00OO0OO00O0O0 .get ('attributes'):#line:1442
                if (OO0O00O0000O00O0O .get ('name'),None )==None :#line:1443
                    print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O} has no 'name' attribute specified.")#line:1444
                    O000O000OO0O0O0O0 =False #line:1445
                    return O000O000OO0O0O0O0 #line:1446
                if not ((OO0O00O0000O00O0O .get ('name'))in O00O0OOOO0OOO00O0 .data ["varname"]):#line:1447
                    print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O.get('name')} not in variable list. Please check spelling.")#line:1448
                    O000O000OO0O0O0O0 =False #line:1449
                    return O000O000OO0O0O0O0 #line:1450
                if (OO0O00O0000O00O0O .get ('type'),None )==None :#line:1451
                    print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O.get('name')} has no 'type' attribute specified.")#line:1452
                    O000O000OO0O0O0O0 =False #line:1453
                    return O000O000OO0O0O0O0 #line:1454
                if not ((OO0O00O0000O00O0O .get ('type'))in (['rcut','lcut','seq','subset','one'])):#line:1455
                    print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O.get('name')} has unsupported type {OO0O00O0000O00O0O.get('type')}. Supported types are 'subset','seq','lcut','rcut','one'.")#line:1456
                    O000O000OO0O0O0O0 =False #line:1457
                    return O000O000OO0O0O0O0 #line:1458
                if (OO0O00O0000O00O0O .get ('minlen'),None )==None :#line:1459
                    print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O.get('name')} has no minimal length specified.")#line:1460
                    O000O000OO0O0O0O0 =False #line:1461
                    return O000O000OO0O0O0O0 #line:1462
                if not (type (OO0O00O0000O00O0O .get ('minlen'))is int ):#line:1463
                    if not (OO0O00O0000O00O0O .get ('type')=='one'):#line:1464
                        print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O.get('name')} has invalid type of minimal length.")#line:1465
                        O000O000OO0O0O0O0 =False #line:1466
                        return O000O000OO0O0O0O0 #line:1467
                if (OO0O00O0000O00O0O .get ('maxlen'),None )==None :#line:1468
                    print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O.get('name')} has no maximal length specified.")#line:1469
                    O000O000OO0O0O0O0 =False #line:1470
                    return O000O000OO0O0O0O0 #line:1471
                if not (type (OO0O00O0000O00O0O .get ('maxlen'))is int ):#line:1472
                    if not (OO0O00O0000O00O0O .get ('type')=='one'):#line:1473
                        print (f"Error: cedent {O00OO0OOO0OO000OO} / attribute {OO0O00O0000O00O0O.get('name')} has invalid type of maximal length.")#line:1474
                        O000O000OO0O0O0O0 =False #line:1475
                        return O000O000OO0O0O0O0 #line:1476
        return O000O000OO0O0O0O0 #line:1477
    def _calculate (OOOO0O00OOO0O0OO0 ,**O0O0O0O0O0O00000O ):#line:1479
        if OOOO0O00OOO0O0OO0 .data ["data_prepared"]==0 :#line:1480
            print ("Error: data not prepared")#line:1481
            return #line:1482
        OOOO0O00OOO0O0OO0 .kwargs =O0O0O0O0O0O00000O #line:1483
        OOOO0O00OOO0O0OO0 .proc =O0O0O0O0O0O00000O .get ('proc')#line:1484
        OOOO0O00OOO0O0OO0 .quantifiers =O0O0O0O0O0O00000O .get ('quantifiers')#line:1485
        OOOO0O00OOO0O0OO0 ._init_task ()#line:1487
        OOOO0O00OOO0O0OO0 .stats ['start_proc_time']=time .time ()#line:1488
        OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do']=[]#line:1489
        OOOO0O00OOO0O0OO0 .task_actinfo ['cedents']=[]#line:1490
        if O0O0O0O0O0O00000O .get ("proc")=='UICMiner':#line:1493
            if not (OOOO0O00OOO0O0OO0 ._check_cedents (['ante'],**O0O0O0O0O0O00000O )):#line:1494
                return #line:1495
            _OOO0OO0O0OO0O0O00 =O0O0O0O0O0O00000O .get ("cond")#line:1497
            if _OOO0OO0O0OO0O0O00 !=None :#line:1498
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1499
            else :#line:1500
                O000OO0O0O0O00000 =OOOO0O00OOO0O0OO0 .cedent #line:1501
                O000OO0O0O0O00000 ['cedent_type']='cond'#line:1502
                O000OO0O0O0O00000 ['filter_value']=(1 <<OOOO0O00OOO0O0OO0 .data ["rows_count"])-1 #line:1503
                O000OO0O0O0O00000 ['generated_string']='---'#line:1504
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1506
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents'].append (O000OO0O0O0O00000 )#line:1507
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('ante')#line:1508
            if O0O0O0O0O0O00000O .get ('target',None )==None :#line:1509
                print ("ERROR: no succedent/target variable defined for UIC Miner")#line:1510
                return #line:1511
            if not (O0O0O0O0O0O00000O .get ('target')in OOOO0O00OOO0O0OO0 .data ["varname"]):#line:1512
                print ("ERROR: target parameter is not variable. Please check spelling of variable name in parameter 'target'.")#line:1513
                return #line:1514
            if ("aad_score"in OOOO0O00OOO0O0OO0 .quantifiers ):#line:1515
                if not ("aad_weights"in OOOO0O00OOO0O0OO0 .quantifiers ):#line:1516
                    print ("ERROR: for aad quantifier you need to specify aad weights.")#line:1517
                    return #line:1518
                if not (len (OOOO0O00OOO0O0OO0 .quantifiers .get ("aad_weights"))==len (OOOO0O00OOO0O0OO0 .data ["dm"][OOOO0O00OOO0O0OO0 .data ["varname"].index (OOOO0O00OOO0O0OO0 .kwargs .get ('target'))])):#line:1519
                    print ("ERROR: aad weights has different number of weights than classes of target variable.")#line:1520
                    return #line:1521
        elif O0O0O0O0O0O00000O .get ("proc")=='CFMiner':#line:1522
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do']=['cond']#line:1523
            if O0O0O0O0O0O00000O .get ('target',None )==None :#line:1524
                print ("ERROR: no target variable defined for CF Miner")#line:1525
                return #line:1526
            if not (OOOO0O00OOO0O0OO0 ._check_cedents (['cond'],**O0O0O0O0O0O00000O )):#line:1527
                return #line:1528
            if not (O0O0O0O0O0O00000O .get ('target')in OOOO0O00OOO0O0OO0 .data ["varname"]):#line:1529
                print ("ERROR: target parameter is not variable. Please check spelling of variable name in parameter 'target'.")#line:1530
                return #line:1531
            if ("aad"in OOOO0O00OOO0O0OO0 .quantifiers ):#line:1532
                if not ("aad_weights"in OOOO0O00OOO0O0OO0 .quantifiers ):#line:1533
                    print ("ERROR: for aad quantifier you need to specify aad weights.")#line:1534
                    return #line:1535
                if not (len (OOOO0O00OOO0O0OO0 .quantifiers .get ("aad_weights"))==len (OOOO0O00OOO0O0OO0 .data ["dm"][OOOO0O00OOO0O0OO0 .data ["varname"].index (OOOO0O00OOO0O0OO0 .kwargs .get ('target'))])):#line:1536
                    print ("ERROR: aad weights has different number of weights than classes of target variable.")#line:1537
                    return #line:1538
        elif O0O0O0O0O0O00000O .get ("proc")=='4ftMiner':#line:1541
            if not (OOOO0O00OOO0O0OO0 ._check_cedents (['ante','succ'],**O0O0O0O0O0O00000O )):#line:1542
                return #line:1543
            _OOO0OO0O0OO0O0O00 =O0O0O0O0O0O00000O .get ("cond")#line:1545
            if _OOO0OO0O0OO0O0O00 !=None :#line:1546
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1547
            else :#line:1548
                O000OO0O0O0O00000 =OOOO0O00OOO0O0OO0 .cedent #line:1549
                O000OO0O0O0O00000 ['cedent_type']='cond'#line:1550
                O000OO0O0O0O00000 ['filter_value']=(1 <<OOOO0O00OOO0O0OO0 .data ["rows_count"])-1 #line:1551
                O000OO0O0O0O00000 ['generated_string']='---'#line:1552
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1554
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents'].append (O000OO0O0O0O00000 )#line:1555
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('ante')#line:1559
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('succ')#line:1560
        elif O0O0O0O0O0O00000O .get ("proc")=='NewAct4ftMiner':#line:1561
            _OOO0OO0O0OO0O0O00 =O0O0O0O0O0O00000O .get ("cond")#line:1564
            if _OOO0OO0O0OO0O0O00 !=None :#line:1565
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1566
            else :#line:1567
                O000OO0O0O0O00000 =OOOO0O00OOO0O0OO0 .cedent #line:1568
                O000OO0O0O0O00000 ['cedent_type']='cond'#line:1569
                O000OO0O0O0O00000 ['filter_value']=(1 <<OOOO0O00OOO0O0OO0 .data ["rows_count"])-1 #line:1570
                O000OO0O0O0O00000 ['generated_string']='---'#line:1571
                print (O000OO0O0O0O00000 ['filter_value'])#line:1572
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1573
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents'].append (O000OO0O0O0O00000 )#line:1574
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('antv')#line:1575
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('sucv')#line:1576
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('ante')#line:1577
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('succ')#line:1578
        elif O0O0O0O0O0O00000O .get ("proc")=='Act4ftMiner':#line:1579
            _OOO0OO0O0OO0O0O00 =O0O0O0O0O0O00000O .get ("cond")#line:1582
            if _OOO0OO0O0OO0O0O00 !=None :#line:1583
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1584
            else :#line:1585
                O000OO0O0O0O00000 =OOOO0O00OOO0O0OO0 .cedent #line:1586
                O000OO0O0O0O00000 ['cedent_type']='cond'#line:1587
                O000OO0O0O0O00000 ['filter_value']=(1 <<OOOO0O00OOO0O0OO0 .data ["rows_count"])-1 #line:1588
                O000OO0O0O0O00000 ['generated_string']='---'#line:1589
                print (O000OO0O0O0O00000 ['filter_value'])#line:1590
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1591
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents'].append (O000OO0O0O0O00000 )#line:1592
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('antv-')#line:1593
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('antv+')#line:1594
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('sucv-')#line:1595
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('sucv+')#line:1596
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('ante')#line:1597
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('succ')#line:1598
        elif O0O0O0O0O0O00000O .get ("proc")=='SD4ftMiner':#line:1599
            if not (OOOO0O00OOO0O0OO0 ._check_cedents (['ante','succ','frst','scnd'],**O0O0O0O0O0O00000O )):#line:1602
                return #line:1603
            _OOO0OO0O0OO0O0O00 =O0O0O0O0O0O00000O .get ("cond")#line:1604
            if _OOO0OO0O0OO0O0O00 !=None :#line:1605
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1606
            else :#line:1607
                O000OO0O0O0O00000 =OOOO0O00OOO0O0OO0 .cedent #line:1608
                O000OO0O0O0O00000 ['cedent_type']='cond'#line:1609
                O000OO0O0O0O00000 ['filter_value']=(1 <<OOOO0O00OOO0O0OO0 .data ["rows_count"])-1 #line:1610
                O000OO0O0O0O00000 ['generated_string']='---'#line:1611
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('cond')#line:1613
                OOOO0O00OOO0O0OO0 .task_actinfo ['cedents'].append (O000OO0O0O0O00000 )#line:1614
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('frst')#line:1615
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('scnd')#line:1616
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('ante')#line:1617
            OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do'].append ('succ')#line:1618
        else :#line:1619
            print ("Unsupported procedure")#line:1620
            return #line:1621
        print ("Will go for ",O0O0O0O0O0O00000O .get ("proc"))#line:1622
        OOOO0O00OOO0O0OO0 .task_actinfo ['optim']={}#line:1625
        OO0OO0OO0O00OO00O =True #line:1626
        for OO0OO0OO00O0O00O0 in OOOO0O00OOO0O0OO0 .task_actinfo ['cedents_to_do']:#line:1627
            try :#line:1628
                O00OOO0OO0OOOO0O0 =OOOO0O00OOO0O0OO0 .kwargs .get (OO0OO0OO00O0O00O0 )#line:1629
                if O00OOO0OO0OOOO0O0 .get ('type')!='con':#line:1633
                    OO0OO0OO0O00OO00O =False #line:1634
            except :#line:1636
                O0O0O0O0OOO0000O0 =1 <2 #line:1637
        if OOOO0O00OOO0O0OO0 .options ['optimizations']==False :#line:1639
            OO0OO0OO0O00OO00O =False #line:1640
        OOOO0OOO0O0OOOO00 ={}#line:1641
        OOOO0OOO0O0OOOO00 ['only_con']=OO0OO0OO0O00OO00O #line:1642
        OOOO0O00OOO0O0OO0 .task_actinfo ['optim']=OOOO0OOO0O0OOOO00 #line:1643
        print ("Starting to mine rules.")#line:1651
        sys .stdout .flush ()#line:1652
        time .sleep (0.01 )#line:1653
        if OOOO0O00OOO0O0OO0 .options ['progressbar']:#line:1654
            O0000O0OOO00O0O00 =[progressbar .Percentage (),progressbar .Bar (),progressbar .Timer ()]#line:1655
            OOOO0O00OOO0O0OO0 .bar =progressbar .ProgressBar (widgets =O0000O0OOO00O0O00 ,max_value =100 ,fd =sys .stdout ).start ()#line:1656
            OOOO0O00OOO0O0OO0 .bar .update (0 )#line:1657
        OOOO0O00OOO0O0OO0 .progress_lower =0 #line:1658
        OOOO0O00OOO0O0OO0 .progress_upper =100 #line:1659
        OOOO0O00OOO0O0OO0 ._start_cedent (OOOO0O00OOO0O0OO0 .task_actinfo ,OOOO0O00OOO0O0OO0 .progress_lower ,OOOO0O00OOO0O0OO0 .progress_upper )#line:1660
        if OOOO0O00OOO0O0OO0 .options ['progressbar']:#line:1661
            OOOO0O00OOO0O0OO0 .bar .update (100 )#line:1662
            OOOO0O00OOO0O0OO0 .bar .finish ()#line:1663
        OOOO0O00OOO0O0OO0 .stats ['end_proc_time']=time .time ()#line:1665
        print ("Done. Total verifications : "+str (OOOO0O00OOO0O0OO0 .stats ['total_cnt'])+", rules "+str (OOOO0O00OOO0O0OO0 .stats ['total_valid'])+", times: prep "+"{:.2f}".format (OOOO0O00OOO0O0OO0 .stats ['end_prep_time']-OOOO0O00OOO0O0OO0 .stats ['start_prep_time'])+"sec, processing "+"{:.2f}".format (OOOO0O00OOO0O0OO0 .stats ['end_proc_time']-OOOO0O00OOO0O0OO0 .stats ['start_proc_time'])+"sec")#line:1669
        O0O000O0O0OOO0OO0 ={}#line:1670
        OO0OO00O0O0O0O0O0 ={}#line:1671
        OO0OO00O0O0O0O0O0 ["task_type"]=O0O0O0O0O0O00000O .get ('proc')#line:1672
        OO0OO00O0O0O0O0O0 ["target"]=O0O0O0O0O0O00000O .get ('target')#line:1674
        OO0OO00O0O0O0O0O0 ["self.quantifiers"]=OOOO0O00OOO0O0OO0 .quantifiers #line:1675
        if O0O0O0O0O0O00000O .get ('cond')!=None :#line:1677
            OO0OO00O0O0O0O0O0 ['cond']=O0O0O0O0O0O00000O .get ('cond')#line:1678
        if O0O0O0O0O0O00000O .get ('ante')!=None :#line:1679
            OO0OO00O0O0O0O0O0 ['ante']=O0O0O0O0O0O00000O .get ('ante')#line:1680
        if O0O0O0O0O0O00000O .get ('succ')!=None :#line:1681
            OO0OO00O0O0O0O0O0 ['succ']=O0O0O0O0O0O00000O .get ('succ')#line:1682
        if O0O0O0O0O0O00000O .get ('opts')!=None :#line:1683
            OO0OO00O0O0O0O0O0 ['opts']=O0O0O0O0O0O00000O .get ('opts')#line:1684
        O0O000O0O0OOO0OO0 ["taskinfo"]=OO0OO00O0O0O0O0O0 #line:1685
        O00OOOOOO00O0000O ={}#line:1686
        O00OOOOOO00O0000O ["total_verifications"]=OOOO0O00OOO0O0OO0 .stats ['total_cnt']#line:1687
        O00OOOOOO00O0000O ["valid_rules"]=OOOO0O00OOO0O0OO0 .stats ['total_valid']#line:1688
        O00OOOOOO00O0000O ["total_verifications_with_opt"]=OOOO0O00OOO0O0OO0 .stats ['total_ver']#line:1689
        O00OOOOOO00O0000O ["time_prep"]=OOOO0O00OOO0O0OO0 .stats ['end_prep_time']-OOOO0O00OOO0O0OO0 .stats ['start_prep_time']#line:1690
        O00OOOOOO00O0000O ["time_processing"]=OOOO0O00OOO0O0OO0 .stats ['end_proc_time']-OOOO0O00OOO0O0OO0 .stats ['start_proc_time']#line:1691
        O00OOOOOO00O0000O ["time_total"]=OOOO0O00OOO0O0OO0 .stats ['end_prep_time']-OOOO0O00OOO0O0OO0 .stats ['start_prep_time']+OOOO0O00OOO0O0OO0 .stats ['end_proc_time']-OOOO0O00OOO0O0OO0 .stats ['start_proc_time']#line:1692
        O0O000O0O0OOO0OO0 ["summary_statistics"]=O00OOOOOO00O0000O #line:1693
        O0O000O0O0OOO0OO0 ["rules"]=OOOO0O00OOO0O0OO0 .rulelist #line:1694
        OOOOO0OO0O00OOOO0 ={}#line:1695
        OOOOO0OO0O00OOOO0 ["varname"]=OOOO0O00OOO0O0OO0 .data ["varname"]#line:1696
        OOOOO0OO0O00OOOO0 ["catnames"]=OOOO0O00OOO0O0OO0 .data ["catnames"]#line:1697
        O0O000O0O0OOO0OO0 ["datalabels"]=OOOOO0OO0O00OOOO0 #line:1698
        OOOO0O00OOO0O0OO0 .result =O0O000O0O0OOO0OO0 #line:1699
    def print_summary (OO0OO0OO00OO00O00 ):#line:1701
        print ("")#line:1702
        print ("CleverMiner task processing summary:")#line:1703
        print ("")#line:1704
        print (f"Task type : {OO0OO0OO00OO00O00.result['taskinfo']['task_type']}")#line:1705
        print (f"Number of verifications : {OO0OO0OO00OO00O00.result['summary_statistics']['total_verifications']}")#line:1706
        print (f"Number of rules : {OO0OO0OO00OO00O00.result['summary_statistics']['valid_rules']}")#line:1707
        print (f"Total time needed : {strftime('%Hh %Mm %Ss', gmtime(OO0OO0OO00OO00O00.result['summary_statistics']['time_total']))}")#line:1708
        print (f"Time of data preparation : {strftime('%Hh %Mm %Ss', gmtime(OO0OO0OO00OO00O00.result['summary_statistics']['time_prep']))}")#line:1710
        print (f"Time of rule mining : {strftime('%Hh %Mm %Ss', gmtime(OO0OO0OO00OO00O00.result['summary_statistics']['time_processing']))}")#line:1711
        print ("")#line:1712
    def print_hypolist (OO0O0OO0O0OOOOO0O ):#line:1714
        OO0O0OO0O0OOOOO0O .print_rulelist ();#line:1715
    def print_rulelist (OOOOOOO000O0O0OO0 ,sortby =None ,storesorted =False ):#line:1717
        def OO0OO0O000OOOOOOO (OO00O00O000OO000O ):#line:1718
            OOOOO000OOOO0O000 =OO00O00O000OO000O ["params"]#line:1719
            return OOOOO000OOOO0O000 .get (sortby ,0 )#line:1720
        print ("")#line:1722
        print ("List of rules:")#line:1723
        if OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="4ftMiner":#line:1724
            print ("RULEID BASE  CONF  AAD    Rule")#line:1725
        elif OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="UICMiner":#line:1726
            print ("RULEID BASE  AAD_SCORE  Rule")#line:1727
        elif OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="CFMiner":#line:1728
            print ("RULEID BASE  S_UP  S_DOWN Condition")#line:1729
        elif OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1730
            print ("RULEID BASE1 BASE2 RatioConf DeltaConf Rule")#line:1731
        else :#line:1732
            print ("Unsupported task type for rulelist")#line:1733
            return #line:1734
        OO0OO0000OO00OO00 =OOOOOOO000O0O0OO0 .result ["rules"]#line:1735
        if sortby is not None :#line:1736
            OO0OO0000OO00OO00 =sorted (OO0OO0000OO00OO00 ,key =OO0OO0O000OOOOOOO ,reverse =True )#line:1737
            if storesorted :#line:1738
                OOOOOOO000O0O0OO0 .result ["rules"]=OO0OO0000OO00OO00 #line:1739
        for OOO0O00O0OOOO0000 in OO0OO0000OO00OO00 :#line:1741
            OOO0000O00OOOOOO0 ="{:6d}".format (OOO0O00O0OOOO0000 ["rule_id"])#line:1742
            if OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="4ftMiner":#line:1743
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +" "+"{:5d}".format (OOO0O00O0OOOO0000 ["params"]["base"])+" "+"{:.3f}".format (OOO0O00O0OOOO0000 ["params"]["conf"])+" "+"{:+.3f}".format (OOO0O00O0OOOO0000 ["params"]["aad"])#line:1745
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +" "+OOO0O00O0OOOO0000 ["cedents_str"]["ante"]+" => "+OOO0O00O0OOOO0000 ["cedents_str"]["succ"]+" | "+OOO0O00O0OOOO0000 ["cedents_str"]["cond"]#line:1746
            elif OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="UICMiner":#line:1747
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +" "+"{:5d}".format (OOO0O00O0OOOO0000 ["params"]["base"])+" "+"{:.3f}".format (OOO0O00O0OOOO0000 ["params"]["aad_score"])#line:1748
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +"     "+OOO0O00O0OOOO0000 ["cedents_str"]["ante"]+" => "+OOOOOOO000O0O0OO0 .result ['taskinfo']['target']+"(*) | "+OOO0O00O0OOOO0000 ["cedents_str"]["cond"]#line:1749
            elif OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="CFMiner":#line:1750
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +" "+"{:5d}".format (OOO0O00O0OOOO0000 ["params"]["base"])+" "+"{:5d}".format (OOO0O00O0OOOO0000 ["params"]["s_up"])+" "+"{:5d}".format (OOO0O00O0OOOO0000 ["params"]["s_down"])#line:1751
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +" "+OOO0O00O0OOOO0000 ["cedents_str"]["cond"]#line:1752
            elif OOOOOOO000O0O0OO0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1753
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +" "+"{:5d}".format (OOO0O00O0OOOO0000 ["params"]["base1"])+" "+"{:5d}".format (OOO0O00O0OOOO0000 ["params"]["base2"])+"    "+"{:.3f}".format (OOO0O00O0OOOO0000 ["params"]["ratioconf"])+"    "+"{:+.3f}".format (OOO0O00O0OOOO0000 ["params"]["deltaconf"])#line:1754
                OOO0000O00OOOOOO0 =OOO0000O00OOOOOO0 +"  "+OOO0O00O0OOOO0000 ["cedents_str"]["ante"]+" => "+OOO0O00O0OOOO0000 ["cedents_str"]["succ"]+" | "+OOO0O00O0OOOO0000 ["cedents_str"]["cond"]+" : "+OOO0O00O0OOOO0000 ["cedents_str"]["frst"]+" x "+OOO0O00O0OOOO0000 ["cedents_str"]["scnd"]#line:1755
            print (OOO0000O00OOOOOO0 )#line:1757
        print ("")#line:1758
    def print_hypo (O0O000O00O0OO00O0 ,O0OO00O00000O0000 ):#line:1760
        O0O000O00O0OO00O0 .print_rule (O0OO00O00000O0000 )#line:1761
    def print_rule (OOO00OOOO00OOOOOO ,O0O000OOO0OOOO00O ):#line:1764
        print ("")#line:1765
        if (O0O000OOO0OOOO00O <=len (OOO00OOOO00OOOOOO .result ["rules"])):#line:1766
            if OOO00OOOO00OOOOOO .result ['taskinfo']['task_type']=="4ftMiner":#line:1767
                print ("")#line:1768
                OO0OOO0O0O000O000 =OOO00OOOO00OOOOOO .result ["rules"][O0O000OOO0OOOO00O -1 ]#line:1769
                print (f"Rule id : {OO0OOO0O0O000O000['rule_id']}")#line:1770
                print ("")#line:1771
                print (f"Base : {'{:5d}'.format(OO0OOO0O0O000O000['params']['base'])}  Relative base : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['rel_base'])}  CONF : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['conf'])}  AAD : {'{:+.3f}'.format(OO0OOO0O0O000O000['params']['aad'])}  BAD : {'{:+.3f}'.format(OO0OOO0O0O000O000['params']['bad'])}")#line:1772
                print ("")#line:1773
                print ("Cedents:")#line:1774
                print (f"  antecedent : {OO0OOO0O0O000O000['cedents_str']['ante']}")#line:1775
                print (f"  succcedent : {OO0OOO0O0O000O000['cedents_str']['succ']}")#line:1776
                print (f"  condition  : {OO0OOO0O0O000O000['cedents_str']['cond']}")#line:1777
                print ("")#line:1778
                print ("Fourfold table")#line:1779
                print (f"    |  S  |  ¬S |")#line:1780
                print (f"----|-----|-----|")#line:1781
                print (f" A  |{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold'][0])}|{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold'][1])}|")#line:1782
                print (f"----|-----|-----|")#line:1783
                print (f"¬A  |{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold'][2])}|{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold'][3])}|")#line:1784
                print (f"----|-----|-----|")#line:1785
            elif OOO00OOOO00OOOOOO .result ['taskinfo']['task_type']=="CFMiner":#line:1786
                print ("")#line:1787
                OO0OOO0O0O000O000 =OOO00OOOO00OOOOOO .result ["rules"][O0O000OOO0OOOO00O -1 ]#line:1788
                print (f"Rule id : {OO0OOO0O0O000O000['rule_id']}")#line:1789
                print ("")#line:1790
                OOOO0OO00O00OO0OO =""#line:1791
                if ('aad'in OO0OOO0O0O000O000 ['params']):#line:1792
                    OOOO0OO00O00OO0OO ="aad : "+str (OO0OOO0O0O000O000 ['params']['aad'])#line:1793
                print (f"Base : {'{:5d}'.format(OO0OOO0O0O000O000['params']['base'])}  Relative base : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['rel_base'])}  Steps UP (consecutive) : {'{:5d}'.format(OO0OOO0O0O000O000['params']['s_up'])}  Steps DOWN (consecutive) : {'{:5d}'.format(OO0OOO0O0O000O000['params']['s_down'])}  Steps UP (any) : {'{:5d}'.format(OO0OOO0O0O000O000['params']['s_any_up'])}  Steps DOWN (any) : {'{:5d}'.format(OO0OOO0O0O000O000['params']['s_any_down'])}  Histogram maximum : {'{:5d}'.format(OO0OOO0O0O000O000['params']['max'])}  Histogram minimum : {'{:5d}'.format(OO0OOO0O0O000O000['params']['min'])}  Histogram relative maximum : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['rel_max'])} Histogram relative minimum : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['rel_min'])} {OOOO0OO00O00OO0OO}")#line:1795
                print ("")#line:1796
                print (f"Condition  : {OO0OOO0O0O000O000['cedents_str']['cond']}")#line:1797
                print ("")#line:1798
                O0OO0O0OOOOOOO000 =OOO00OOOO00OOOOOO .get_category_names (OOO00OOOO00OOOOOO .result ["taskinfo"]["target"])#line:1799
                print (f"Categories in target variable  {O0OO0O0OOOOOOO000}")#line:1800
                print (f"Histogram                      {OO0OOO0O0O000O000['params']['hist']}")#line:1801
                if ('aad'in OO0OOO0O0O000O000 ['params']):#line:1802
                    print (f"Histogram on full set          {OO0OOO0O0O000O000['params']['hist_full']}")#line:1803
                    print (f"Relative histogram             {OO0OOO0O0O000O000['params']['rel_hist']}")#line:1804
                    print (f"Relative histogram on full set {OO0OOO0O0O000O000['params']['rel_hist_full']}")#line:1805
            elif OOO00OOOO00OOOOOO .result ['taskinfo']['task_type']=="UICMiner":#line:1806
                print ("")#line:1807
                OO0OOO0O0O000O000 =OOO00OOOO00OOOOOO .result ["rules"][O0O000OOO0OOOO00O -1 ]#line:1808
                print (f"Rule id : {OO0OOO0O0O000O000['rule_id']}")#line:1809
                print ("")#line:1810
                OOOO0OO00O00OO0OO =""#line:1811
                if ('aad_score'in OO0OOO0O0O000O000 ['params']):#line:1812
                    OOOO0OO00O00OO0OO ="aad score : "+str (OO0OOO0O0O000O000 ['params']['aad_score'])#line:1813
                print (f"Base : {'{:5d}'.format(OO0OOO0O0O000O000['params']['base'])}  Relative base : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['rel_base'])}   {OOOO0OO00O00OO0OO}")#line:1815
                print ("")#line:1816
                print (f"Condition  : {OO0OOO0O0O000O000['cedents_str']['cond']}")#line:1817
                print (f"Antecedent : {OO0OOO0O0O000O000['cedents_str']['ante']}")#line:1818
                print ("")#line:1819
                print (f"Histogram                                        {OO0OOO0O0O000O000['params']['hist']}")#line:1820
                if ('aad_score'in OO0OOO0O0O000O000 ['params']):#line:1821
                    print (f"Histogram on full set with condition             {OO0OOO0O0O000O000['params']['hist_cond']}")#line:1822
                    print (f"Relative histogram                               {OO0OOO0O0O000O000['params']['rel_hist']}")#line:1823
                    print (f"Relative histogram on full set with condition    {OO0OOO0O0O000O000['params']['rel_hist_cond']}")#line:1824
                O00O0O0O0000O000O =OOO00OOOO00OOOOOO .result ['datalabels']['catnames'][OOO00OOOO00OOOOOO .result ['datalabels']['varname'].index (OOO00OOOO00OOOOOO .result ['taskinfo']['target'])]#line:1825
                print (" ")#line:1827
                print ("Interpretation:")#line:1828
                for OO0O0OO000OOOOO0O in range (len (O00O0O0O0000O000O )):#line:1829
                  O0O00OOO000000OO0 =0 #line:1830
                  if OO0OOO0O0O000O000 ['params']['rel_hist'][OO0O0OO000OOOOO0O ]>0 :#line:1831
                      O0O00OOO000000OO0 =OO0OOO0O0O000O000 ['params']['rel_hist'][OO0O0OO000OOOOO0O ]/OO0OOO0O0O000O000 ['params']['rel_hist_cond'][OO0O0OO000OOOOO0O ]#line:1832
                  O00O0OO0O00OO0OO0 =''#line:1833
                  if not (OO0OOO0O0O000O000 ['cedents_str']['cond']=='---'):#line:1834
                      O00O0OO0O00OO0OO0 ="For "+OO0OOO0O0O000O000 ['cedents_str']['cond']+": "#line:1835
                  print (f"    {O00O0OO0O00OO0OO0}{OOO00OOOO00OOOOOO.result['taskinfo']['target']}({O00O0O0O0000O000O[OO0O0OO000OOOOO0O]}) has occurence {'{:.1%}'.format(OO0OOO0O0O000O000['params']['rel_hist_cond'][OO0O0OO000OOOOO0O])}, with antecedent it has occurence {'{:.1%}'.format(OO0OOO0O0O000O000['params']['rel_hist'][OO0O0OO000OOOOO0O])}, that is {'{:.3f}'.format(O0O00OOO000000OO0)} times more.")#line:1837
            elif OOO00OOOO00OOOOOO .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1838
                print ("")#line:1839
                OO0OOO0O0O000O000 =OOO00OOOO00OOOOOO .result ["rules"][O0O000OOO0OOOO00O -1 ]#line:1840
                print (f"Rule id : {OO0OOO0O0O000O000['rule_id']}")#line:1841
                print ("")#line:1842
                print (f"Base1 : {'{:5d}'.format(OO0OOO0O0O000O000['params']['base1'])} Base2 : {'{:5d}'.format(OO0OOO0O0O000O000['params']['base2'])}  Relative base 1 : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['rel_base1'])} Relative base 2 : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['rel_base2'])} CONF1 : {'{:.3f}'.format(OO0OOO0O0O000O000['params']['conf1'])}  CONF2 : {'{:+.3f}'.format(OO0OOO0O0O000O000['params']['conf2'])}  Delta Conf : {'{:+.3f}'.format(OO0OOO0O0O000O000['params']['deltaconf'])} Ratio Conf : {'{:+.3f}'.format(OO0OOO0O0O000O000['params']['ratioconf'])}")#line:1843
                print ("")#line:1844
                print ("Cedents:")#line:1845
                print (f"  antecedent : {OO0OOO0O0O000O000['cedents_str']['ante']}")#line:1846
                print (f"  succcedent : {OO0OOO0O0O000O000['cedents_str']['succ']}")#line:1847
                print (f"  condition  : {OO0OOO0O0O000O000['cedents_str']['cond']}")#line:1848
                print (f"  first set  : {OO0OOO0O0O000O000['cedents_str']['frst']}")#line:1849
                print (f"  second set : {OO0OOO0O0O000O000['cedents_str']['scnd']}")#line:1850
                print ("")#line:1851
                print ("Fourfold tables:")#line:1852
                print (f"FRST|  S  |  ¬S |  SCND|  S  |  ¬S |");#line:1853
                print (f"----|-----|-----|  ----|-----|-----| ")#line:1854
                print (f" A  |{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold1'][0])}|{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold1'][1])}|   A  |{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold2'][0])}|{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold2'][1])}|")#line:1855
                print (f"----|-----|-----|  ----|-----|-----|")#line:1856
                print (f"¬A  |{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold1'][2])}|{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold1'][3])}|  ¬A  |{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold2'][2])}|{'{:5d}'.format(OO0OOO0O0O000O000['params']['fourfold2'][3])}|")#line:1857
                print (f"----|-----|-----|  ----|-----|-----|")#line:1858
            else :#line:1859
                print ("Unsupported task type for rule details")#line:1860
            print ("")#line:1864
        else :#line:1865
            print ("No such rule.")#line:1866
    def get_rulecount (OOO0O0OOOO0O00OO0 ):#line:1868
        return len (OOO0O0OOOO0O00OO0 .result ["rules"])#line:1869
    def get_fourfold (O00O0OO00000OO0O0 ,O00OOOOOO0OOOOOOO ,order =0 ):#line:1871
        if (O00OOOOOO0OOOOOOO <=len (O00O0OO00000OO0O0 .result ["rules"])):#line:1873
            if O00O0OO00000OO0O0 .result ['taskinfo']['task_type']=="4ftMiner":#line:1874
                O00O0O0O0O00OOOOO =O00O0OO00000OO0O0 .result ["rules"][O00OOOOOO0OOOOOOO -1 ]#line:1875
                return O00O0O0O0O00OOOOO ['params']['fourfold']#line:1876
            elif O00O0OO00000OO0O0 .result ['taskinfo']['task_type']=="CFMiner":#line:1877
                print ("Error: fourfold for CFMiner is not defined")#line:1878
                return None #line:1879
            elif O00O0OO00000OO0O0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1880
                O00O0O0O0O00OOOOO =O00O0OO00000OO0O0 .result ["rules"][O00OOOOOO0OOOOOOO -1 ]#line:1881
                if order ==1 :#line:1882
                    return O00O0O0O0O00OOOOO ['params']['fourfold1']#line:1883
                if order ==2 :#line:1884
                    return O00O0O0O0O00OOOOO ['params']['fourfold2']#line:1885
                print ("Error: for SD4ft-Miner, you need to provide order of fourfold table in order= parameter (valid values are 1,2).")#line:1886
                return None #line:1887
            else :#line:1888
                print ("Unsupported task type for rule details")#line:1889
        else :#line:1890
            print ("No such rule.")#line:1891
    def get_hist (O00000OO00O0OO000 ,O00OO0O00OOO0OO00 ):#line:1893
        if (O00OO0O00OOO0OO00 <=len (O00000OO00O0OO000 .result ["rules"])):#line:1895
            if O00000OO00O0OO000 .result ['taskinfo']['task_type']=="CFMiner":#line:1896
                OO000OOO00O0OO0OO =O00000OO00O0OO000 .result ["rules"][O00OO0O00OOO0OO00 -1 ]#line:1897
                return OO000OOO00O0OO0OO ['params']['hist']#line:1898
            elif O00000OO00O0OO000 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1899
                print ("Error: SD4ft-Miner has no histogram")#line:1900
                return None #line:1901
            elif O00000OO00O0OO000 .result ['taskinfo']['task_type']=="4ftMiner":#line:1902
                print ("Error: 4ft-Miner has no histogram")#line:1903
                return None #line:1904
            else :#line:1905
                print ("Unsupported task type for rule details")#line:1906
        else :#line:1907
            print ("No such rule.")#line:1908
    def get_hist_cond (OO00O0OO0000OOOOO ,OOO0OO00000O0OOOO ):#line:1911
        if (OOO0OO00000O0OOOO <=len (OO00O0OO0000OOOOO .result ["rules"])):#line:1913
            if OO00O0OO0000OOOOO .result ['taskinfo']['task_type']=="UICMiner":#line:1914
                OOOO00000OOO00000 =OO00O0OO0000OOOOO .result ["rules"][OOO0OO00000O0OOOO -1 ]#line:1915
                return OOOO00000OOO00000 ['params']['hist_cond']#line:1916
            elif OO00O0OO0000OOOOO .result ['taskinfo']['task_type']=="CFMiner":#line:1917
                OOOO00000OOO00000 =OO00O0OO0000OOOOO .result ["rules"][OOO0OO00000O0OOOO -1 ]#line:1918
                return OOOO00000OOO00000 ['params']['hist']#line:1919
            elif OO00O0OO0000OOOOO .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1920
                print ("Error: SD4ft-Miner has no histogram")#line:1921
                return None #line:1922
            elif OO00O0OO0000OOOOO .result ['taskinfo']['task_type']=="4ftMiner":#line:1923
                print ("Error: 4ft-Miner has no histogram")#line:1924
                return None #line:1925
            else :#line:1926
                print ("Unsupported task type for rule details")#line:1927
        else :#line:1928
            print ("No such rule.")#line:1929
    def get_quantifiers (O0O00O00OO00OOOO0 ,OOOOO0OO00000OO0O ,order =0 ):#line:1931
        if (OOOOO0OO00000OO0O <=len (O0O00O00OO00OOOO0 .result ["rules"])):#line:1933
            O0O0O0OOOO000OO0O =O0O00O00OO00OOOO0 .result ["rules"][OOOOO0OO00000OO0O -1 ]#line:1934
            if O0O00O00OO00OOOO0 .result ['taskinfo']['task_type']=="4ftMiner":#line:1935
                return O0O0O0OOOO000OO0O ['params']#line:1936
            elif O0O00O00OO00OOOO0 .result ['taskinfo']['task_type']=="CFMiner":#line:1937
                return O0O0O0OOOO000OO0O ['params']#line:1938
            elif O0O00O00OO00OOOO0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:1939
                return O0O0O0OOOO000OO0O ['params']#line:1940
            else :#line:1941
                print ("Unsupported task type for rule details")#line:1942
        else :#line:1943
            print ("No such rule.")#line:1944
    def get_varlist (O0O0OOO00O000OO0O ):#line:1946
        return O0O0OOO00O000OO0O .result ["datalabels"]["varname"]#line:1947
    def get_category_names (OOOOOO00O00O000OO ,varname =None ,varindex =None ):#line:1949
        OO0O0OOO0O0000O00 =0 #line:1950
        if varindex is not None :#line:1951
            if OO0O0OOO0O0000O00 >=0 &OO0O0OOO0O0000O00 <len (OOOOOO00O00O000OO .get_varlist ()):#line:1952
                OO0O0OOO0O0000O00 =varindex #line:1953
            else :#line:1954
                print ("Error: no such variable.")#line:1955
                return #line:1956
        if (varname is not None ):#line:1957
            OO0000OOOO000OOOO =OOOOOO00O00O000OO .get_varlist ()#line:1958
            OO0O0OOO0O0000O00 =OO0000OOOO000OOOO .index (varname )#line:1959
            if OO0O0OOO0O0000O00 ==-1 |OO0O0OOO0O0000O00 <0 |OO0O0OOO0O0000O00 >=len (OOOOOO00O00O000OO .get_varlist ()):#line:1960
                print ("Error: no such variable.")#line:1961
                return #line:1962
        return OOOOOO00O00O000OO .result ["datalabels"]["catnames"][OO0O0OOO0O0000O00 ]#line:1963
    def print_data_definition (O0OOOO00OOOO0OOOO ):#line:1965
        O0O0OOOO0O0OO00OO =O0OOOO00OOOO0OOOO .get_varlist ()#line:1966
        for OOO0OO000OOO0O0O0 in O0O0OOOO0O0OO00OO :#line:1967
            OO0OOO0OO0O00OOOO =O0OOOO00OOOO0OOOO .get_category_names (OOO0OO000OOO0O0O0 )#line:1968
            O0O000O00000000O0 =""#line:1969
            for O0O0O00O00OO0OOO0 in OO0OOO0OO0O00OOOO :#line:1970
                O0O000O00000000O0 =O0O000O00000000O0 +str (O0O0O00O00OO0OOO0 )+" "#line:1971
            O0O000O00000000O0 =O0O000O00000000O0 [:-1 ]#line:1972
            print (f"Variable {OOO0OO000OOO0O0O0} has {len(O0O0OOOO0O0OO00OO)} categories: {O0O000O00000000O0}")#line:1973
