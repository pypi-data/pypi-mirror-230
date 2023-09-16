message:    outp=<OUTFILE>.o   runtpe=<OUTFILE>.r

c cell cards
 1     0           -10 -1
 2     0           -10  2
 5     <MATERIAL>      1 -2 -10
 10    0            10 

c surface cards
 1     px 0
 2     px <THICKNESS>
 10    box -500 -500 -500 1000 0 0 0 1000 0 0 0 1000

mode  p
imp:p   1 1 1 0
m1    1000            0.666657 $ Water -0.998207
      8000            0.333343
m2    82000           1.000000 $ Lead  -11.35
m3    6000            0.000150 $ Air   -0.001205
      7000            0.784431
      8000            0.210748
      18000           0.004671
m4    1000            0.305330 $ Ordinary Concrete (NIST) -2.3
      6000            0.002880
      8000            0.500407 
      11000           0.009212 
      12000           0.000725 
      13000           0.010298 
      14000           0.151042
      19000           0.003578
      20000           0.014924 
      26000           0.001605
m5    1000            0.109602 $ Barite Concrete  -3.35
      8000            0.600189
      12000           0.001515 
      13000           0.004777 
      14000           0.011473
      16000           0.103654
      20000           0.038593 
      26000           0.026213
      56000           0.103983
m6    1000            0.333321 $ Gypsum (Plaster of Paris)
      8000            0.500014 $ Density varies significantly
      16000           0.083324 $ Knauf Standard: 0.66 g/cm3
      20000           0.083341 $ Knauf Safeboard: 1.40 g/cm3
m7    8000            0.663432 $ Brick, Common Silica   -1.8
      13000           0.003747
      14000           0.323225
      20000           0.007063
      26000           0.002534
m8    74000           1.000000 $ Tungsten  -19.3
c
sdef pos=-200 0 0 erg=<SDEF>
c
e5   .001 1998I 2
f5:p 200 0 0 0 ND
c df5 ic 31 iu 2 LOG fac 1
nps <NPS>
c STOP F5 0.1
rand seed=<RAND_SEED>
