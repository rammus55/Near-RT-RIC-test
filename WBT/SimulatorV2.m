%clear all;

function [sendBLER, sendSINR, sendLatency, sendThroughput, choiceDLUL, sendRBs] = SimulatorV2(input_dic)
   action = struct(input_dic);

rng('shuffle');
%Downlink or Uplink
choiceDLUL = 1;
if choiceDLUL == 1
    Txpower = 40;
else
    Txpower = 20;
end
nxn = 2000;                 %n*n空間大小(m)
number_UE = 15;             %UE 個數
number_BS = 3;              %基站個數
PLmodel = 2;                %choice Path Loss Model
GrantfreeInd = 0;           %Grantfree
mmaxHARQ = 32;
times = 1;                  %幾次平均
Transmissiondata = 32*8;    %UE傳送data量   32bytes*8 = 256bits
fc = 3;
c = 3e+8;
mu = 0;

%BLER   MCS 0~28   SNR -15~33                                        
BLER = [0.9     0.8     0.7     0.6     0.52    0.48    0.4     0.32    0.23    0.19    0.15    9.8*10^-2   7*10^-2     4.2*10^-2   3*10^-2     1.7*10^-2   1*10^-2     7*10^-3     3*10^-3     4*10^-4     1*10^-4     1*10^-5     1*10^-5     1*10^-5     1*10^-5     1*10^-5      1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       0.9     0.8     0.7     0.6     0.56    0.5     0.41    0.32    0.28    0.2     1.7*10^-1   0.1         6.5*10^-2   4.5*10^-2   3*10^-2     2.3*10^-2   1.2*10^-2   4.2*10^-3   2*10^-3     7*10^-4     9*10^-5     2*10^-5     1*10^-5     1*10^-5     1*10^-5      1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       0.95    0.9     0.85    0.8     0.7     0.58    0.49    0.4     0.35    0.28    0.1         0.16        0.1         7*10^-2     4.8*10^-2   3*10^-2     2*10^-2     9*10^-3     5*10^-3     1.5*10^-3   2*10^-4     4.5*10^-5   1*10^-5     1*10^-5     1*10^-5      1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       0.95    0.9     0.85    0.75    0.62    0.53    0.45    0.4     0.32    0.26        0.2         0.14        0.1         7*10^-2     4.9*10^-2   3*10^-2     1.6*10^-2   9*10^-3     5*10^-3     2*10^-3     1*10^-3     1.5*10^-4   2.5*10^-5   1*10^-5      1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       0.95    0.9     0.8     0.7     0.6     0.5     0.45    0.39    0.31        0.25        0.18        0.14        9.5*10^-2   6.7*10^-2   4*10^-2     2*10^-2     1.5*10^-2   8.5*10^-3   4*10^-3     2*10^-3     3.5*10^-4   6*10^-5     1*10^-5      1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       0.95    0.85    0.8     0.7     0.6     0.55    0.48    0.4         0.32        0.23        0.18        0.14        9*10^-2     6.3*10^-2   3.5*10^-2   2.5*10^-2   1.8*10^-2   9*10^-3     5*10^-3     9*10^-4     1.9*10^-4   3*10^-5      1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       0.9     0.85    0.8     0.7     0.62    0.57    0.49        0.4         0.3         0.23        0.18        1.3*10^-1   8*10^-2     5*10^-2     3.5*10^-2   2.8*10^-2   1.5*10^-2   8*10^-1     1*10^-3     4.5*10^-4   1*10^-4      2.5*10^-5    1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       0.95    0.9     0.85    0.8     0.7     0.6     0.55        0.46        0.36        0.29        0.23        1.8*10^-1   1.3*10^-1   8*10^-2     6*10^-2     4*10^-2     2.5*10^-2   1.6*10^-2   7*10^-3     3*10^-3     1.8*10^-3    1*10^-3      4*10^-4      8.5*10^-5  2*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5    1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       0.95    0.9     0.85    0.77    0.7     0.61        0.51        0.41        0.34        0.29        2.2*10^-1   1.7*10^-1   1.2*10^-1   8*10^-2     6.6*10^-2   3.4*10^-2   2.3*10^-2   1.3*10^-2   6*10^-3     3.7*10^-3    2*10^-3      9*10^-4      2.3*10^-4  5*10^-5    1*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1       0.95    0.9     0.83    0.75    0.68        0.6         0.5         0.41        0.37        3*10^-1     2.2*10^-1   1.5*10^-1   1.2*10^-1   8.5*10^-2   5.5*10^-2   3.8*10^-2   2.3*10^-2   1.4*10^-2   8*10^-3      4*10^-3      2*10^-3      5*10^-4    1.4*10^-4  3*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      0.95    0.9     0.8     0.72        0.67        0.58        0.5         0.42        3.6*10^-1   2.7*10^-1   1.8*10^-1   1.5*10^-1   1.2*10^-1   7*10^-2     5*10^-2     3.3*10^-2   2*10^-2     1.3*10^-2    6*10^-3      3*10^-3      1*10^-3    2.8*10^-4  5*10^-5    1*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       0.95    0.9     0.8         0.7         0.65        0.55        0.48        0.4         0.34        0.25        0.2         0.16        0.1         7.5*10^-2   5*10^-2     3*10^-2     1.9*10^-2    1.2*10^-2    5.5*10^-3    1.9*10^-3  5*10^-4    5*10^-4    2*10^-5      1*10^-5      1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       0.95    0.9         0.8         0.7         0.6         0.52        0.45        0.4         0.31        0.25        0.19        0.13        9.8*10^-2   6*10^-2     4*10^-2     2.5*10^-2    1.6*10^-2    8.3*10^-3    2.7*10^-3  1*10^-3    2.5*10^-4  4.5*10^-5    1.5*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       0.95        0.9         0.8         0.7         0.6         0.5         0.45        0.36        0.28        0.22        0.16        0.12        8*10^-2     5.5*10^-2   3.8*10^-2    2.5*10^-2    1.5*10^-2    6.1*10^-3  2.5*10^-3  8*10^-4    2*10^-4      5.6*10^-5    1.7*10^-5  1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           0.95        0.9         0.8         0.7         0.58        0.5         0.4         0.3         0.25        0.18        0.15        0.1         7*10^-2     5*10^-2      3.5*10^-2    2*10^-2      1*10^-2    4.1*10^-3  1.7*10^-3  3.5*10^-4    1.3*10^-4    4*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           0.95        0.9         0.8         0.63        0.58        0.45        0.4         0.3         0.23        0.18        0.14        9.5*10^-2   7*10^-2      5*10^-2      3*10^-2      1.9*10^-2  8.2*10^-3  2.5*10^-3  6.5*10^-4    2.1*10^-4    7*10^-5    2*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           0.95        0.9         0.7         0.65        0.55        0.47        0.38        0.3         0.25        0.18        0.13        8.8*10^-2    7*10^-2      4.1*10^-2    2.8*10^-2  1.3*10^-2  4*10^-4    1*10^-3      4*10^-4      1.5*10^-4  4*10^-5    1*10^-5    1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           0.6         0.5         0.4         0.35        0.3         0.2         0.16        0.12         0.09         0.078        0.038      0.02       0.01       4.8*10^-3    2*10^-3      2.1*10^-4  5*10^-5    1.8*10^-5  1*10^-5    1*10^-5    1*10^-5   1*10^-5   1*10^-5	 1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5; 
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           0.6         0.5         0.4         0.35        0.28        0.2         0.15         0.1          0.09         0.048      0.028      0.017      0.0098       4*10^-3      1*10^-3    2.5*10^-4  8*10^-5    1.5*10^-5  1*10^-5    1*10^-5   1*10^-5   1*10^-5     1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           0.55        0.45        0.42        0.3         0.25        0.2          0.15         0.12         0.075      0.05       0.032      0.022        0.014        4*10^-3    7*10^-4    2.8*10^-4  4.5*10^-5  1*10^-5    1*10^-5   1*10^-5   1*10^-5     1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           0.6         0.51        0.5         0.38        0.3         0.25         0.2          0.15         0.1        0.07       0.05       0.035        0.022        8*10^-3    2*10^-3    9*10^-4    2*10^-4    4.5*10^-5  1*10^-5   1*10^-5   1*10^-5     1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           0.6         0.55        0.43        0.35        0.3          0.25         0.2          0.15       0.1        0.07       0.05         0.03         0.017      6*10^-3    3*10^-3    6*10^-4    1.7*10^-4  2.5*10^-5 1*10^-5   1*10^-5     1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           1           0.65        0.5         0.4         0.35         0.3          0.25         0.18       0.14       0.09       0.065        0.04         0.024      1*10^-3    6*10^-3    1.5*10^-3  4*10^-4    8*10^-5   2.3*10^-5 1*10^-5     1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           1           1           0.7         0.55        0.47         0.4          0.32         0.25       0.18       0.13       0.09         0.065        0.038      0.02       0.014      6*10^-3    4*10^-3    1.6*10^-3 7*10^-4   2.5*10^-4   1*10^-5     1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           1           1           1           0.7         0.58         0.5          0.4          0.3        0.22       0.17       0.13         0.085        0.05       0.03       0.02       0.012      7*10^-3    3*10^-3   1.5*10^-3 5*10^-4     1.6*10^-4   1*10^-5     1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           1           1           1           1           0.7          0.53         0.45         0.35       0.25       0.19       0.15         0.095        0.06       0.04       0.03       0.018      0.013      5.5*10^-3 2.8*10^-3 1.3*10^-3   4.5*10^-4   1.5*10^-4   4*10^-5   1.3*10^-5 1*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           1           1           1           1           1            0.65         0.5          0.38       0.28       0.2        0.16         0.11         0.072      0.05       0.04       0.025      0.017      8*10^-3   4*10^-3   2*10^-3     1.2*10^-3   4.5*10^-4   1.5*10^-4 4*10^-5   2*10^-5   1*10^-5   1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           1           1           1           1           1            0.78         0.65         0.5        0.42       0.37       0.31         0.265        0.2        0.16       0.13       0.09       0.065      0.04      0.028     1.8*10^-2   1*10^-2     6*10^-3     2.8*10^-3 1.5*10^-3 6*10^-4   1.9*10^-4 1*10^-5   1*10^-5;
        1       1       1       1       1       1       1        1      1       1       1       1           1           1           1           1           1           1           1           1           1           1           1           1           1           1            0.8          0.7          0.68       0.6        0.51       0.48         0.4          0.32       0.28       0.22       0.16       0.12       0.07      0.05      3.2*10^-2   2*10^-2     1.2*10^-2   5.2*10^-3 3*10^-3   1.3*10^-3 4*10^-4   1.8*10^-4 1*10^-5;];


%選擇頻寬和Numerology
%SCS = input('輸入Subcarrier Spacing(kHz)是多少(15、30、60、120)?');
SCS = 15;
FR1 = [25 52 79 106 133 160 216 270 0 0 0; 
       11 24 38 51 65 78 106 133 162 217 273; 
       0 11 18 24 31 38 51 65 79 107 135];
FR2 = [66 132 264 0;
       32 66 132 264];
bandwidth1 = [5 10 15 20 25 30 40 50 60 80 100];
bandwidth2 = [50 100 200 400];
if SCS == 15
    scs = 1;
    %BW = input('輸入頻寬(MHz)多大(5、10、15、20、25、30、40、50、60、80、100)\n若是5請輸入1、10輸入2 以此類推?');
    BW = 4;
    RB = FR1(scs,BW);
elseif SCS == 30
    scs = 2;
    BW = input('輸入頻寬(MHz)多大(5、10、15、20、25、30、40、50、60、80、100)\n若是5請輸入1、10輸入2 以此類推?');
    RB = FR1(scs,BW);
elseif SCS == 60
    choicefr = input('輸入是用FR1還是FR2(FR1請輸入1、FR2輸入2)?');
    if choicefr == 1
        scs = 3;
        BW = input('輸入頻寬(MHz)多大(5、10、15、20、25、30、40、50、60、80、100)\n若是5請輸入1、10輸入2 以此類推?');
        RB = FR1(scs,BW);
    else
        scs = 1;
        BW = input('輸入頻寬(MHz)多大(50、100、200、400)\n若是50請輸入1、100輸入2 以此類推?');
        RB = FR2(scs,BW);
    end
else
    scs = 2;
    BW = input('輸入頻寬(MHz)多大(50、100、200、400)\n若是50請輸入1、100輸入2 以此類推?');
    RB = FR2(scs,BW);
end

%Small Scale Fading 參數
fs = 1000000;
Slot = 1; %Slot = input('UE需要跑多久slot(ms)？');
Cluster = 20;
ResultCluster = 30;
Antenna_Tx = 1;
Antenna_Rx = 1;
velocity = 3*1000/3600; %v = input('UE移動速度(km/hr)？');

theta_BS = 30;
theta_BS = theta_BS/180*pi;
theta_MS = 45;
theta_MS = theta_MS/180*pi;
lamda = 0.12; %%(3*10^8)/(2.5*10^9);
d_BS = 4*lamda;
d_MS = 0.5*lamda;
Cluster_ASD = 2; 
Cluster_ASD = Cluster_ASD/180*pi;
Cluster_ASA = 15;
Cluster_ASA = Cluster_ASA/180*pi;
Cluster_Delay = [0 60 75 145 150 190 220 335 370 430 510 685 725 735 800 960 1020 1100 1210 1845];
Cluster_Power_dB = [-6.4 -3.4 -2 -3 -1.9 -3.4 -3.4 -4.6 -7.8 -7.8 -9.3 -12 -8.5 -13.2 -11.2 -20.8 -14.5 -11.7 -17.2 -16.7];   
Cluster_Power = 10.^(Cluster_Power_dB./10);
Cluster_AOD = [11 -8 -6 0 6 8 -12 -9 -12 -12 13 15 -12 -15 -14 19 -16 15 18 17];
Cluster_AOD = Cluster_AOD/180*pi;
Cluster_AOA = [61 44 -34 0 33 -44 -67 52 -67 -67 -73 -83 -70 87 80 109 91 -82 99 98];
Cluster_AOA = Cluster_AOA/180*pi;
delta_k = [0.0447 -0.0447 0.1413 -0.1413 0.2492 -0.2492 0.3715 -0.3715 0.5129 -0.5129 0.6797 -0.6797 0.8844 -0.8844 1.1481 -1.1481 1.5195 -1.5195 2.1551 -2.1551];
f_max = velocity/lamda;
%N0 = 512;
N0 = 128;


%存Data的矩陣
distance = zeros(number_BS,number_UE);
PLnlos = zeros(number_BS,number_UE);
PLlos = zeros(number_BS,number_UE);
PL = zeros(number_BS,number_UE);
rc_PL = zeros(number_BS,number_UE);
rc_PL_SH = zeros(number_BS,number_UE);
Shadowing = zeros(number_BS,number_UE,Slot);
LSF = zeros(number_BS,number_UE,Slot);
Allocation = zeros(1,number_UE);
Mindistance = zeros(1,number_UE);
allocation = 1;
SSFdB = zeros(number_BS,number_UE,Slot);
resultfading = zeros(number_BS,number_UE,Slot);
finalpowerdB = zeros(number_BS,number_UE,Slot);
finalpowerW = zeros(number_BS,number_UE,Slot);
numberservice = zeros(number_BS,1);
SSF_perSlot = zeros(number_BS,number_UE,Slot);
total_SSF = zeros(number_BS,number_UE);
interferencepower = zeros(1,number_UE,Slot,times);
Finalpower = zeros(1,number_UE,Slot,times);
SINR45 = zeros(1,number_UE,mmaxHARQ);
BLER_UE = zeros(1,number_UE,Slot,mmaxHARQ);
CountHARQ = zeros(1,number_UE);
totalSINR = zeros(1,number_UE);

%分配基站&UE的(x,y)
%rng('default');
rng(5);
for ue = 1 : number_UE
    location_UE_x(ue) = rand*nxn;
    location_UE_y(ue) = rand*nxn;
end
for bs = 1 : number_BS
    location_BS_x(bs) = rand*nxn;
    location_BS_y(bs) = rand*nxn;
end
rng('shuffle');

%{
%BS&UE位置圖
figure(1);
ss = scatter(location_UE_x,location_UE_y,'filled');
ss.LineWidth = 0.6;
ss.MarkerFaceColor = 'b';
hold on
ss = scatter(location_BS_x,location_BS_y,'filled');
ss.LineWidth = 0.6;
ss.MarkerFaceColor = 'r';
hold off
xlabel('X distance(m)');
ylabel('Y distance(m)');
legend('User Equipment (UE)','Base station (BS)');
title('UE & BS location')
%}

%計算UE&基站距離
distancetest = zeros(1,number_UE);
ServiceFive = zeros(1,number_BS);
for bs = 1 : number_BS
    for ue = 1 : number_UE
        distance(bs,ue) = sqrt((location_UE_x(ue) - location_BS_x(bs))^2 + (location_UE_y(ue) - location_BS_y(bs))^2);
        distancetest(1,ue) = distance(1,ue);
    end
end

%分配UE由哪個基站服務
for ue = 1 : number_UE
    Mindistance(1,ue) = 20000;
    for bs = 1 : number_BS
        if ServiceFive(1,bs) ~= 5
            if Mindistance(1,ue) > distance(bs,ue)
                Allocation(1,ue) = bs;
                Mindistance(1,ue) = distance(bs,ue);
            end
        end
    end
    ServiceFive(1,Allocation(1,ue)) = ServiceFive(1,Allocation(1,ue)) + 1;
end

%設定repetition

repetition1 = action.Repetition1;
repetition2 = action.Repetition2;
repetition3 = action.Repetition3;
repetition4 = action.Repetition4;
repetition5 = action.Repetition5;

%{
repetition1 = 1;
repetition2 = 1;
repetition3 = 1;
repetition4 = 1;
repetition5 = 1;
%}

Tr_repetition = zeros(1,number_UE);
repetition = zeros(1,number_UE);
%Tr_repetition = Transmissiondata * repetition;
countset = 1;
for ue = 1 : number_UE
    if Allocation(1,ue) == 1
        if countset == 1
            repetition(1,ue) = repetition1;
            countset = countset + 1;
        elseif countset == 2
            repetition(1,ue) = repetition2;
            countset = countset + 1;
        elseif countset == 3
            repetition(1,ue) = repetition3;
            countset = countset + 1;
        elseif countset == 4
            repetition(1,ue) = repetition4;
            countset = countset + 1;
        elseif countset == 5
            repetition(1,ue) = repetition5;
            countset = countset + 1;
        end
    else
        repetition(1,ue) = 1;
    end
    Tr_repetition(1,ue) = Transmissiondata * repetition(1,ue);
end

coderate = [120 157 193 251 308 379 449 526 602 679 340 378 434 490 553 616 658 438 466 517 567 616 666 719 772 822 873 910 948];
%設定mcs

mcs1 = action.MCS1;
mcs2 = action.MCS2;
mcs3 = action.MCS3;
mcs4 = action.MCS4;
mcs5 = action.MCS5;

%{
mcs1 = 28;
mcs2 = 28;
mcs3 = 28;
mcs4 = 28;
mcs5 = 28;
%}


MCS_UE = zeros(1,number_UE);
RBbits = zeros(1,number_UE);
useRBs = zeros(1,number_UE);
countset = 1;
for ue = 1 : number_UE
    if Allocation(1,ue) == 1
        if countset == 1
            MCS_UE(1,ue) = mcs1;
            countset = countset + 1;
        elseif countset == 2
            MCS_UE(1,ue) = mcs2;
            countset = countset + 1;
        elseif countset == 3
            MCS_UE(1,ue) = mcs3;
            countset = countset + 1;
        elseif countset == 4
            MCS_UE(1,ue) = mcs4;
            countset = countset + 1;
        elseif countset == 5
            MCS_UE(1,ue) = mcs5;
            countset = countset + 1;
        end
    else
        MCS_UE(1,ue) = 17;
    end
    RBbits(1,ue) = fix(12*14*6*(coderate(MCS_UE(1,ue)+1)/1024));
    useRBs(1,ue) = ceil(Tr_repetition(1,ue)/RBbits(1,ue));
end

%設定harq

harq1 = action.HARQ1;
harq2 = action.HARQ2;
harq3 = action.HARQ3;
harq4 = action.HARQ4;
harq5 = action.HARQ5;

%{
harq1 = 4;
harq2 = 4;
harq3 = 4;
harq4 = 4;
harq5 = 4;
%}

HARQ = zeros(1,number_UE);
countset = 1;
for ue = 1 : number_UE
    if Allocation(1,ue) == 1
        if countset == 1
            HARQ(1,ue) = harq1;
            countset = countset + 1;
        elseif countset == 2
            HARQ(1,ue) = harq2;
            countset = countset + 1;
        elseif countset == 3
            HARQ(1,ue) = harq3;
            countset = countset + 1;
        elseif countset == 4
            HARQ(1,ue) = harq4;
            countset = countset + 1;
        elseif countset == 5
            HARQ(1,ue) = harq5;
            countset = countset + 1;
        end
    else
        HARQ(1,ue) = 2;
    end
end
maxHARQ = 0;
for ue = 1 : number_UE
    if HARQ(1,ue) > maxHARQ
        maxHARQ = HARQ(1,ue);
    end
end



%選擇&設定PassLoss Modal
%PLmodel = input('Path loss model 1:RMa(Rural Macro), 2:UMa(Urban Macro), 3:UMi(Urban Micro), 4:InH(Indoor Hotspot) ？');
%los_nlos = input('LOS or NLOS 1:LOS(Line Of Sight), 2:NLOS(Non-LOS)？');
if PLmodel == 1 %RMa
    Hut = 1.5;
    Hbs = 35;
    for bs = 1 : number_BS
        for ue = 1 : number_UE
            if distance(bs,ue) > 10
                PrLOS_NLOS = exp(-(distance(bs,ue)-10)/1000);
                t = rand;
                if t <= PrLOS_NLOS
                    los_nlos = 1;
                else
                    los_nlos = 2;
                end
            else
                los_nlos = 1;
            end
        end
    end
elseif PLmodel == 2 %UMa
    Hut = 1.8;
    Hbs = 25; 
    for bs = 1 : number_BS
        for ue = 1 : number_UE
            if distance(bs,ue) > 18
                if Hut <= 13
                    Cprime = 0;
                else
                    Cprime = ((Hut-13)/10)^1.5;
                end
                PrLOS_NLOS = (18/distance(bs,ue) + exp(-(distance(bs,ue)/63)*(1-18/distance(bs,ue)))) * (1+Cprime*(5/4)*(distance(bs,ue)/100)^3*exp(-(distance(bs,ue)/150)));
                t = rand;
                if t <= PrLOS_NLOS
                    los_nlos = 1;
                else
                    los_nlos = 2;
                end
            else
                los_nlos = 1;
            end
        end
    end
elseif PLmodel == 3 %UMi
    Hut = 1.8;
    Hbs = 10; 
    for bs = 1 : number_BS
        for ue = 1 : number_UE
            if distance(bs,ue) > 18
                PrLOS_NLOS = (18/distance(bs,ue)) + exp(-(distance(bs,ue)/36)*(1-18/distance(bs,ue)));
                t = rand;
                if t <= PrLOS_NLOS
                    los_nlos = 1;
                else
                    los_nlos = 2;
                end
            else
                los_nlos = 1;
            end
        end
    end
else %InH
    Hut = 1.8;
    Hbs = 25; 
    for bs = 1 : number_BS
        for ue = 1 : number_UE
            if distance(bs,ue) > 6.5
                PrLOS_NLOS = exp(-(distance(bs,ue)-6.5)/32.6) * 0.32;
                t = rand;
                if t <= PrLOS_NLOS
                    los_nlos = 1;
                else
                    los_nlos = 2;
                end
            elseif distance(bs,ue) <= 1.2
                los_nlos = 1;
            else
                PrLOS_NLOS = exp(-(distance(bs,ue)-1.2)/4.7);
                t = rand;
                if t <= PrLOS_NLOS
                    los_nlos = 1;
                else
                    los_nlos = 2;
                end
            end
        end
    end
end
hight = Hbs - Hut;

%Resource Block轉成SubCarrier number
SubCarrierNumber = zeros(1,number_UE);

%Transport block
TransportBlock = zeros(1,number_UE);
for ue = 1 : number_UE
   SubCarrierNumber(1,ue) = 12*useRBs(1,ue);
   TransportBlock(1,ue) = 256 * repetition(1,ue);
end

%分配subcarrier
totalsub = RB * 12;
interference_sub_slot = zeros(totalsub+1,Slot,number_BS);
sub_start_over = zeros(2,number_UE,Slot); %1存開始 2存結束
counter = 0;
for sloth = 1 : Slot
    for bs = 1 : number_BS
        %counter = 0;
        start = 0;
        over = 0;
        for ue = 1 : number_UE
            if Allocation(1,ue) == bs
                start = 1+counter;
                over = SubCarrierNumber(1,ue)+counter;
                if over > totalsub
                    start = 1;
                    over = SubCarrierNumber(1,ue);
                    count = SubCarrierNumber(1,ue);
                end
                for subcount = start : over
                    interference_sub_slot(subcount,sloth,bs) = ue;
                end
                counter = counter + SubCarrierNumber(1,ue);
                %start
                sub_start_over(1,ue,sloth) = start;
                %over
                sub_start_over(2,ue,sloth) = over;
            end
        end
    end
end

%subcarrier_power = zeros(totalsub,Slot,number_BS);
subcarrierpower = zeros(number_BS,number_UE,RB*12,Slot);
%subcarrierpower(bs,ue,numsubcarrier,sloth)


%Latency
Latency = zeros(1,number_UE);
reTrans = zeros(1,number_UE);
Throughput = zeros(1,32);
button = 1;
harqcount = 0;
while button ~= 0 && harqcount < maxHARQ %重傳迴圈
    harqcount = harqcount + 1; %傳送錯誤 重傳次數+1 
    %Path Loss & Shadowing &SSF
    for time = 1 : times
        uesave = zeros(1,number_UE);
        for bs = 1 : number_BS
            for ue = 1 : number_UE
                SubCarrier = SubCarrierNumber(1,ue);
                total_subcarrier_slot = zeros(SubCarrier,Slot);
                avg_subcarrier_slot = zeros(SubCarrier,Slot);
                %SSF = 0;
                D2 = distance(bs,ue);
                D3 = sqrt(D2*D2 + hight*hight);
                %RMa
                if PLmodel == 1
                    h = 5;
                    W = 20;
                    %LOS
                    dBP = 2*pi*Hbs*Hut*fc*10^9/c;
                    if D2 <= dBP
                        %PL1
                        PLlos(bs,ue) = 20*log10(40*pi*D3*fc/3) + min(0.03*h^1.72,10)*log10(D3) - min(0.044*h^1.72,14.77) + 0.002*log10(h)*D3;
                        sigma = 4;
                    else
                        %PL2
                        PL1 = 20*log10(40*pi*dBP*fc/3) + min(0.03*h^1.72,10)*log10(dBP) - min(0.044*h^1.72,14.77) + 0.002*log10(h)*dBP;
                        PLlos(bs,ue) = PL1 + 40*log10(D3/dBP);
                        sigma = 6;
                    end
                    %NLOS
                    if los_nlos == 2
                        PLpurown = 161.04 - 7.1*log10(W) + 7.5*log10(h) - (24.37-3.7*(h/Hbs)^2)*log10(Hbs) + (43.42-3.1*log10(Hbs))*(log10(D3)-3) + 20*log10(fc) - (3.2*(log10(11.75*Hut))^2 - 4.97);
                        PLnlos(bs,ue) = max(PLlos(bs,ue),PLpurown);
                        %fprintf('Pass loss(基站:%d,UE:%d)=%d dB\n',bs,ue,PLnlos(bs,ue));
                        sigma = 8;
                    end
                %UMa model
                elseif PLmodel == 2
                    %TR 138 901 P.27 Note1
                    if D2 > 18
                        gD2 = (5/4) * (D2/100)^3 * exp(-D2/150);
                    else
                        gD2 = 0;
                    end

                    if Hut < 13
                        C = 0;
                    else
                        C = ((Hut-13)/10)^1.5 * gD2;
                    end

                    probability_he = round((1+C)*10000);
                    pc = randi(probability_he);
                    if pc <= 10000
                        He = 1;
                    else
                        num = (Hut-1.5-12)/3 + 1;
                        for i = 1 : num
                            a(i) = 12 + (i-1)*3;
                        end
                        if rem(num,1) ~= 0
                            nnum = round(num + 1); 
                            a(nnum) = Hut-1.5;
                        else
                            nnum = num;
                        end
                        phe = randi(nnum);
                        He = a(phe);
                    end

                    hpurownBS = Hbs - He;
                    hpurownUT = Hut - He;
                    dpurownBP = 4*hpurownBS*hpurownUT*fc*10^9/c;

                    %LOS
                    if D2 <= dpurownBP
                        %PL1
                        PLlos(bs,ue) = 28.0 + 22*log10(D3) + 20*log10(fc);
                    else
                        %PL2
                        PLlos(bs,ue) = 28.0 + 40*log10(D3) + 20*log10(fc) - 9*log10((dpurownBP^2 + (Hbs-Hut)^2));
                    end
                    sigma = 4;

                    %NLOS
                    if los_nlos == 2
                        PLpurown = 13.54 + 39.08*log10(D3) + 20*log10(fc) - 0.6*(Hut-1.5);
                        PLnlos(bs,ue) = max(PLlos(bs,ue),PLpurown);
                        %fprintf('Pass loss(基站:%d,UE:%d)=%d dB\n',bs,ue,PLnlos(bs,ue));
                        sigma = 6;
                    end
                %UMi
                elseif PLmodel == 3
                    %TR 138 901 P.27 Note1
                    if D2 > 18
                        gD2 = (5/4) * (D2/100)^3 * exp(-D2/150);
                    else
                        gD2 = 0;
                    end

                    if Hut < 13
                        C = 0;
                    else
                        C = ((Hut-13)/10)^1.5 * gD2;
                    end

                    probability_he = round((1+C)*10000);
                    pc = randi(probability_he);
                    if pc <= 10000
                        He = 1;
                    else
                        num = (Hut-1.5-12)/3 + 1;
                        for i = 1 : num
                            a(i) = 12 + (i-1)*3;
                        end
                        if rem(num,1) ~= 0
                            nnum = round(num + 1); 
                            a(nnum) = Hut-1.5;
                        else
                            nnum = num;
                        end
                        phe = randi(nnum);
                        He = a(phe);
                    end

                    hpurownBS = Hbs - He;
                    hpurownUT = Hut - He;
                    dpurownBP = 4*hpurownBS*hpurownUT*fc*10^9/c;
                    %LOS
                    if D2 <= dpurownBP
                        %PL1
                        PLlos(bs,ue) = 32.4 + 21*log10(D3) + 20*log10(fc);
                        sigma = 4;
                    else
                        %PL2
                        PLlos(bs,ue) = 32.4 + 40*log10(D3) + 20*log10(fc) - 9.5*log10(dpurownBP^2+(Hbs-Hut)^2);
                        sigma = 4;
                    end
                    %NLOS
                    if los_nlos == 2
                        PLpurown = 35.3*log10(D3) + 22.4 + 21.3*log10(fc) - 0.3*(Hut-1.5);
                        PLnlos(bs,ue) = max(PLlos(bs,ue),PLpurown);
                        %fprintf('Pass loss(基站:%d,UE:%d)=%d dB\n',bs,ue,PLnlos(bs,ue));
                        sigma = 7.82;
                    end
                %InH
                else
                    %LOS
                    %PL
                    PLlos(bs,ue) = 32.4 + 17.3*log10(D3) + 20*log10(fc);
                    sigma = 3;

                    %NLOS
                    if los_nlos == 2
                        PLpurown = 38.3*log10(D3) + 17.30 + 24.9*log10(fc);
                        PLnlos(bs,ue) = max(PLlos(bs,ue),PLpurown);
                        %fprintf('Pass loss(基站:%d,UE:%d)=%d dB\n',bs,ue,PLnlos(bs,ue));
                        sigma = 8.03;
                    end
                end

                %Shadowing
                for sloth = 1 : Slot
                    %Shadowing(bs,ue,sloth) = lognrnd(mu,sigma);
                    t = randn;
                    %Shadowing(bs,ue,sloth) = exp(t*mu+(t*t*sigma*sigma)/2);
                    Shadowing(bs,ue,sloth) = sigma*t;
                    %Shadowing(bs,ue,sloth) = 3
                    %Shadowing(bs,ue,sloth) = exp(-(log(t)-mu)^2/(2*sigma^2))/(sqrt(2*pi)*sigma*t);
                    %fprintf('Shadowing(基站:%d,UE:%d)=%d dB\n',bs,ue,Shadowing(bs,ue));
                end

                %Large Scale Fading
                if los_nlos == 2
                    %fprintf('Pass loss(基站:%d,UE:%d)=%d dB\n',bs,ue,PLnlos(bs,ue));
                    PL(bs,ue) = PLnlos(bs,ue);
                    for sloth = 1 : Slot
                        LSF(bs,ue,sloth) = PLnlos(bs,ue) + Shadowing(bs,ue,sloth);
                    end
                else
                    %fprintf('Pass loss(基站:%d,UE:%d)=%d dB\n',bs,ue,PLlos(bs,ue));
                    PL(bs,ue) = PLlos(bs,ue);
                    for sloth = 1 : Slot
                        LSF(bs,ue,sloth) = PLlos(bs,ue) + Shadowing(bs,ue,sloth);
                    end
                end

                
                %Small Scale Fading

                % Spatial Correlation Calculation
                temp_a1_BS = zeros(20,1);
                temp_a1_MS = zeros(20,1);
                for k = 1:20
                    temp_a1_BS(k,1) = delta_k(1,k)*Cluster_ASD;
                    temp_a1_MS(k,1) = delta_k(1,k)*Cluster_ASA;
                end
                R_BS = zeros(Cluster,Antenna_Tx,Antenna_Tx);
                R_MS = zeros(Cluster,Antenna_Rx,Antenna_Rx);
                for n = 1:Cluster
                    for p = 1:Antenna_Tx
                        for q = 1:Antenna_Tx
                            for k = 1:20
                                R_BS(n,p,q) = R_BS(n,p,q) + exp(j*(2*pi*d_BS/lamda)*(p-q)*sin(Cluster_AOD(1,n)+temp_a1_BS(k,1)+theta_BS));
                            end
                            R_BS(n,p,q) = R_BS(n,p,q)/20;        
                        end
                    end
                end

                for n = 1:Cluster
                    for p = 1:Antenna_Rx
                        for q = 1:Antenna_Rx
                            for k = 1:20
                                R_MS(n,p,q) = R_MS(n,p,q) + exp(j*(2*pi*d_MS/lamda)*(p-q)*sin(Cluster_AOA(1,n)+temp_a1_MS(k,1)+theta_MS));
                            end
                            R_MS(n,p,q) = R_MS(n,p,q)/20;        
                        end
                    end
                end

                R = zeros(Cluster,Antenna_Tx*Antenna_Rx,Antenna_Tx*Antenna_Rx);
                tempX = zeros(Antenna_Tx,Antenna_Tx);
                tempY = zeros(Antenna_Rx,Antenna_Rx);
                for n = 1:Cluster
                    for p = 1:Antenna_Tx
                        for q = 1:Antenna_Tx        
                            tempX(p,q) = R_BS(n,p,q);
                        end
                    end

                    for p = 1:Antenna_Rx
                        for q = 1:Antenna_Rx        
                            tempY(p,q) = R_MS(n,p,q);
                        end
                    end

                    tempZ = kron(tempX,tempY);

                    for p = 1:Antenna_Tx*Antenna_Rx
                        for q = 1:Antenna_Tx*Antenna_Rx
                            R(n,p,q) = tempZ(p,q);
                        end
                    end
                end

                % Antenna Gain
                Gain = zeros(1,Cluster);
                BS_theta_3db = 70/180*pi;
                MS_theta_3db = 70/180*pi;

                for n = 1:Cluster
                    BS_Gain = -min( 12*( (Cluster_AOD(1,n)+theta_BS)/BS_theta_3db)^2 , 20);
                    MS_Gain = 1;
                    Gain(1,n) = BS_Gain + MS_Gain;
                    Gain(1,n) = 10^(Gain(1,n)/20);
                end

                % Doppler Spectrum - Jake's model
                Had = zeros(Cluster*Antenna_Tx*Antenna_Rx,Cluster*Antenna_Tx*Antenna_Rx);
                Init = [1 1 ; 1 -1];                   %   2 *   2
                Had1 = [Init Init ; Init -Init];       %   4 *   4
                Had2 = [Had1 Had1 ; Had1 -Had1];       %   8 *   8
                Had3 = [Had2 Had2 ; Had2 -Had2];       %  16 *  16
                Had4 = [Had3 Had3 ; Had3 -Had3];       %  32 *  32
                Had5 = [Had4 Had4 ; Had4 -Had4];       %  64 *  64
                Had6 = [Had5 Had5 ; Had5 -Had5];       % 128 * 128
                Had7 = [Had6 Had6 ; Had6 -Had6];       % 256 * 256
                Had8 = [Had7 Had7 ; Had7 -Had7];       % 512 * 512

                Jake_Seq = zeros(Cluster,Antenna_Tx,Antenna_Rx,Slot*SubCarrier);
                theta_index = zeros(N0,1);
                for m = 1:N0
                    theta_index(m,1) = 2*pi*rand;
                end
                for n = 1:Cluster
                    for p = 1:Antenna_Tx
                        for q = 1:Antenna_Rx
                            index = (n-1)*Antenna_Tx*Antenna_Rx+(p-1)*Antenna_Rx+q;
                            for t = 1:Slot*SubCarrier
                                for m = 1:N0
                                    temp = ((2/N0)^0.5)*Had6(index,m)*(cos(pi*m/N0) + j*sin(pi*m/N0))*cos(2*pi*f_max*cos(2*pi*(m-0.5)/512)*t/fs+theta_index(m,1));
                                    Jake_Seq(n,p,q,t) = Jake_Seq(n,p,q,t) + temp;
                                end
                            end
                        end
                    end
                end

                % Create MIMO Channel Matrix
                R_sqrt = zeros(Cluster,Antenna_Tx*Antenna_Rx,Antenna_Tx*Antenna_Rx);
                temp = zeros(Antenna_Tx*Antenna_Rx,Antenna_Tx*Antenna_Rx);

                for n = 1:Cluster
                    for p = 1:Antenna_Tx*Antenna_Rx
                        for q = 1:Antenna_Tx*Antenna_Rx
                            temp(p,q) = R(n,p,q);
                        end
                    end
                    temp2 = temp^0.5;
                    for p = 1:Antenna_Tx*Antenna_Rx
                        for q = 1:Antenna_Tx*Antenna_Rx
                            R_sqrt(n,p,q) = temp2(p,q);
                        end
                    end
                end

                ChannelMatrix = zeros(Cluster,Antenna_Rx,Antenna_Tx,Slot*SubCarrier);
                temp = zeros(Antenna_Tx*Antenna_Rx,1);
                temp2 = zeros(Antenna_Tx*Antenna_Rx,Antenna_Tx*Antenna_Rx);
                temp3 = zeros(Antenna_Tx*Antenna_Rx,1);
                for n = 1:Cluster
                    for t = 1:Slot*SubCarrier
                       for p = 1:Antenna_Tx
                           for q = 1:Antenna_Rx               
                                temp( (p-1)*Antenna_Tx + q,1) = Jake_Seq(n,p,q,t);
                           end
                        end
                        for p = 1:Antenna_Tx*Antenna_Rx
                            for q = 1:Antenna_Tx*Antenna_Rx
                                temp2(p,q) = R_sqrt(n,p,q);     
                            end
                        end
                        temp3 = temp2*temp;
                        for p = 1:Antenna_Tx                
                            for q = 1:Antenna_Rx                
                                ChannelMatrix(n,q,p,t) = temp3( (p-1)*Antenna_Tx+q,1)*Cluster_Power(1,n);     
                            end
                        end
                    end
                end

                IntepolationChannel = zeros(ResultCluster,Antenna_Rx,Antenna_Tx,Slot*SubCarrier);
                for p = 1:Antenna_Tx
                    for q = 1:Antenna_Rx 
                        for rc = 1:ResultCluster        
                            for t = 1:Slot*SubCarrier
                                temp = 0;
                                for c = 1:Cluster
                                    temp = temp + ChannelMatrix(c,q,p,t)*sinc( (rc-1) - Cluster_Delay(c)/10^9*fs );
                                end
                                IntepolationChannel(rc,q,p,t) = temp;
                            end
                        end
                    end
                end

                ReturnChannelCondition = zeros(Slot,ResultCluster,Antenna_Rx,Antenna_Tx,SubCarrier);

                for rc = 1:ResultCluster
                    for t = 1:Slot
                        for p = 1:Antenna_Tx
                            for q = 1:Antenna_Rx   
                                for s = 1:SubCarrier
                                    ReturnChannelCondition(t,rc,q,p,s) = IntepolationChannel(rc,q,p,(t-1)*SubCarrier+s);
                                end
                            end
                        end
                    end
                end

                h = zeros(Antenna_Tx*ResultCluster*SubCarrier,Antenna_Rx,Slot);
                for t = 1:Slot
                    for beta = 1:Antenna_Rx
                        for alpha = 1:Antenna_Tx
                            for rc = 1:ResultCluster
                                for n = 1:SubCarrier
                                    h( (alpha-1)*ResultCluster*SubCarrier+(rc-1)*SubCarrier+n,beta,t) = ReturnChannelCondition(t,rc,beta,alpha,n);
                                    %實部虛部開根號
                                    Re = real(h( (alpha-1)*ResultCluster*SubCarrier+(rc-1)*SubCarrier+n,beta,t));
                                    Im = imag(h( (alpha-1)*ResultCluster*SubCarrier+(rc-1)*SubCarrier+n,beta,t));
                                    %count(t,beta,alpha,rc,n) = (alpha-1)*ResultCluster*SubCarrier+(rc-1)*SubCarrier+n;
                                    ReIm((alpha-1)*ResultCluster*SubCarrier+(rc-1)*SubCarrier+n,beta,t) = sqrt(Re^2 + Im^2);
                                end
                            end
                        end
                    end
                end

                %每個slot中各個subcarrier的總和
                for sloth = 1 : Slot
                    for numbertotal = 1 : SubCarrier * ResultCluster
                        for numsubcarrier = 1 : SubCarrier
                            total_subcarrier_slot(numsubcarrier,sloth) = total_subcarrier_slot(numsubcarrier,sloth) + ReIm(numbertotal,1,sloth)/SubCarrier;
                        end
                    end
                    %平均
                    for numsubcarrier = 1 : SubCarrier
                        avg_subcarrier_slot(numsubcarrier,sloth) = total_subcarrier_slot(numsubcarrier,sloth)/ResultCluster;
                        SSF_perSlot(bs,ue,sloth) = SSF_perSlot(bs,ue,sloth) + avg_subcarrier_slot(numsubcarrier,sloth);
                        subcarrierpower(bs,ue,numsubcarrier,sloth) = avg_subcarrier_slot(numsubcarrier,sloth);
                    end
                    SSFdB(bs,ue,sloth) = 10 * log10(SSF_perSlot(bs,ue,sloth));
                    rc_PL(bs,ue) = Txpower - PL(bs,ue);
                    rc_PL_SH(bs,ue) = Txpower - LSF(bs,ue,sloth);
                    resultfading(bs,ue,sloth) = LSF(bs,ue,sloth) + SSFdB(bs,ue,sloth); 
                    finalpowerdB(bs,ue,sloth) = Txpower - resultfading(bs,ue,sloth); %dB
                    finalpowerW(bs,ue,sloth) = 10^(finalpowerdB(bs,ue,sloth)/10); %W
                end
            end
        end

        %建立每個基站&UE的subcarrier分配表
        re_subcarrier_power_dB = zeros(totalsub,Slot,number_BS,number_BS);
        re_subcarrier_power = zeros(totalsub,Slot,number_BS,number_BS);
        for sloth = 1 : Slot
            for bs2 = 1 : number_BS
                for ue = 1 : number_UE
                    if bs2 == Allocation(1,ue)
                        for bs = 1 : number_BS %bs為UE實際收到的基站 %bs2為UE本來要接收的基站
                            start = sub_start_over(1,ue,1);
                            over = sub_start_over(2,ue,1);
                            countnumsub = 1;
                            for subcount = start : over
                                re_subcarrier_power_dB(subcount,sloth,bs,bs2) = 10*log10(subcarrierpower(bs,ue,countnumsub,sloth));
                                re_subcarrier_power(subcount,sloth,bs,bs2) = 10^(re_subcarrier_power_dB(subcount,sloth,bs,bs2)/10);
                                countnumsub = countnumsub + 1;
                            end
                        end
                    end
                end
            end
        end
        %目標UE的interference power
        %interferencepower = zeros(1,number_UE,Slot,times);
        interferencepower_save = zeros(1,number_UE,Slot,totalsub,number_BS); %最右邊的number_UE不是指UE號碼是站存的號碼
        for sloth = 1 : Slot
            for ue = 1 : number_UE
                save = 1;
                for bs = 1 : number_BS
                    if Allocation(1,ue) ~= bs
                        for numsubcarrier = sub_start_over(1,ue,sloth) : sub_start_over(2,ue,sloth)
                            %interferencepower_save(1,ue,sloth,save) = Txpower - LSF(bs,ue,sloth) - 10*log10(re_subcarrier_power(numsubcarrier,sloth,bs,Allocation(1,ue)));
                            if re_subcarrier_power_dB(numsubcarrier,sloth,Allocation(1,ue),bs) == 0
                                interferencepower_save(1,ue,sloth,save) = 0;
                            else
                                interferencepower_save(1,ue,sloth,save) = Txpower - LSF(bs,ue,sloth) - re_subcarrier_power_dB(numsubcarrier,sloth,Allocation(1,ue),bs);
                                interferencepower_save(1,ue,sloth,save) = 10^(interferencepower_save(1,ue,sloth,save)/10);
                            end
                            save = save + 1;
                        end
                    end
                end
                uesave(1,ue) = save;
            end
        end
        for sloth = 1 : Slot
            for ue = 1 : number_UE
                for saveh = 1 : uesave(1,ue)
                    interferencepower(1,ue,sloth,time) = interferencepower(1,ue,sloth,time) + interferencepower_save(1,ue,sloth,saveh);
                end
                interferencepower(1,ue,sloth,time) = interferencepower(1,ue,sloth,time)/SubCarrierNumber(1,ue);
            end
        end

        %目標UE最後接收power
        %Finalpower = zeros(1,number_UE,Slot,times);
        for sloth = 1 : Slot
            for ue = 1 : number_UE
                for bs = 1 : number_BS
                    if Allocation(1,ue) == bs
                        for numsubcarrier = sub_start_over(1,ue,sloth) : sub_start_over(2,ue,sloth)
                            Finalpower(1,ue,sloth,time) = Finalpower(1,ue,sloth,time) + 10^((Txpower - LSF(bs,ue,sloth) - re_subcarrier_power_dB(numsubcarrier,sloth,bs,Allocation(1,ue)))/10);
                        end
                        Finalpower(1,ue,sloth,time) = Finalpower(1,ue,sloth,time)/SubCarrierNumber(1,ue);
                    end
                end
            end
        end
    end

    %Noise Power
    T = 28 + 273.15; %溫度
    k = 1.38e-23; %波茲曼常數
    Bandwidth = zeros(1,number_UE); %頻寬
    Noisepower = zeros(1,number_UE);
    for ue = 1 : number_UE
        Bandwidth(1,ue) = SCS*SubCarrierNumber(1,ue)*10^3;
        Noisepower(1,ue) = k*T*Bandwidth(1,ue);
    end

    %SINR
    SINR = zeros(1,number_UE,Slot,times);
    for time = 1 : times
        for sloth = 1 : Slot
            for ue = 1 : number_UE
                SINR(1,ue,sloth,time) = 10*log10(Finalpower(1,ue,sloth,time)/(interferencepower(1,ue,sloth,time)+Noisepower(1,ue)));
                %SINR(1,ue,sloth,time) = (Finalpower(1,ue,sloth,time)/(interferencepower(1,ue,sloth,time)+Noisepower(1,ue)));
                SINR(1,ue,sloth,time) = round(SINR(1,ue,sloth,time));
            end
        end
    end

    %avg SINR
    avgSINR = zeros(1,number_UE);
    %SINR45 = zeros(1,number_UE);
    for ue = 1 : number_UE
        count = 0;
        for time = 1 : times
            for sloth = 1 : Slot
                if SINR(1,ue,sloth,time) < -100
                    if SINR(1,ue,sloth,time) == -Inf
                        count = count + 1;
                    else
                        avgSINR(1,ue) = avgSINR(1,ue) - 100;
                    end
                elseif SINR(1,ue,sloth,time) > 100
                    avgSINR(1,ue) = avgSINR(1,ue) + 100;
                else
                    avgSINR(1,ue) = avgSINR(1,ue) + SINR(1,ue,sloth,time);
                end
            end
        end
        avgSINR(1,ue) = (avgSINR(1,ue)/(times-count))/3;
        SINR45(1,ue,harqcount) = round(avgSINR(1,ue));
        %totalSINR(1,ue) = totalSINR(1,ue) + SINR45(1,ue,harqcount);
    end

    %BLER_UE = zeros(1,number_UE,Slot);
    for sloth = 1 : Slot
        for ue = 1 : number_UE
            if avgSINR(1,ue) < -15
                BLER_UE(1,ue,sloth,harqcount) = 1;
            elseif avgSINR(1,ue) > 33
                BLER_UE(1,ue,sloth,harqcount) = 1*10^-5;
            elseif isnan(SINR45(1,ue,harqcount))
                BLER_UE(1,ue,sloth,harqcount) = 0;
            else
                BLER_UE(1,ue,sloth,harqcount) = BLER(MCS_UE(1,ue)+1,SINR45(1,ue,harqcount)+16);
            end
        end
    end
    
    
    successTBs = zeros(number_UE, 3824);
    for sloth = 1 : Slot
        for ue = 1 : number_UE
            %countharq = countharq + 1;
            %successTBs = 0;
            countsucessTBs = 0;
            if harqcount <= HARQ(1,ue)
                if reTrans(1,ue) == 0
                    CountHARQ(1,ue) = CountHARQ(1,ue) + 1;
                    totalSINR(1,ue) = totalSINR(1,ue) + avgSINR(1,ue);
                    if choiceDLUL == 1
                        sd = randi(6);
                        %sd = 4;
                        Latency(1,ue) = Latency(1,ue) + sd;
                    else
                        if GrantfreeInd == 0
                            sd = randi(6);
                            Latency(1,ue) = Latency(1,ue) + sd;
                        end
                    end
                    %{
                    for trb = 1 : TransportBlock(1,ue)
                        Prbler = rand;
                        if Prbler > BLER_UE(1,ue,sloth,harqcount)
                            %successTBs = successTBs + 1;
                            successTBs(ue,trb) = 1;
                        end
                    end
                    %}
                    for rp = 1 : repetition(1,ue)
                        Prbler = rand;
                        if Prbler > BLER_UE(1,ue,sloth)
                            reTrans(1,ue) = 1; %成功傳送
                        end
                    end
                    if reTrans(1,ue) ~= 0
                        if Allocation(1,ue) == 1
                            Throughput(1,harqcount) = Throughput(1,harqcount) + Transmissiondata;
                        end
                    end
                    Latency(1,ue) = Latency(1,ue) + 4;
                end
            end
        end
    end
    %{
    button = 0;
    for ue = 1 : number_UE
        if reTrans(1,ue) == 0
            button = button + 1;
        end
    end
    %}
    
    %只看UE2
    uenumber = 0;
    %whatUEnumber = 0;
    for ue = 1 : number_UE
        %whatUEnumber = whatUEnumber + 1;
        if Allocation(1,ue) == 1
            uenumber = uenumber + 1;
            if uenumber == 2
                if reTrans(1,ue) == 0
                    button = 1;
                else
                    button = 0;
                end
            end
        end
    end
end

distancechoice = zeros(1,number_UE);
for ue = 1 : number_UE
    for bs = 1 : number_BS
        if Allocation(1,ue) == bs
            distancechoice(1,ue) = distance(bs,ue);
        end
    end
end

%send bs1 data to xApp
n = numberservice(1,1);
sendBLER = zeros(1,n);
sendSINR = zeros(1,n);
sendSINR45 = zeros(1,n);
sendLatency = zeros(1,n);
sendThroughput = Throughput(1,1);
sendRBs = zeros(1,n);
q = 1;
for ue = 1 : number_UE
    if Allocation(1,ue) == 1
        %sendBLER(1,q) = BLER_UE(1,ue);
        sendSINR(1,q) = totalSINR(1,ue) / CountHARQ(1,ue);
        %sendBLER(1,q) = BLER(MCS_UE(1,ue)-16,round(sendSINR(1,q)));
        sendLatency(1,q) = Latency(1,ue);
        sendSINR45(1,q) = round(sendSINR(1,q));
        if sendSINR45(1,q) < -15
            sendBLER(1,q) = 1;
        elseif sendSINR45(1,q) > 33
            sendBLER(1,q) = 1*10^-5;
        elseif isnan(sendSINR45(1,q))
            sendBLER(1,q) = 0;
        else
            sendBLER(1,q) = BLER(MCS_UE(1,ue)+1,sendSINR45(1,q)+16);
        end
        sendRBs(1,q) = useRBs(1,ue);
        q = q + 1;
    end
end

%{
%SINR & distance(圖)
if choiceDLUL == 1
    figure(5);
    s5 = scatter(distancechoice,avgSINR,'filled');
    xlabel('distance(m)');
    ylabel('avgSINR');
    title('Downlink avgSINR & distance')
else
    figure(5);
    s5 = scatter(distancechoice,avgSINR,'filled');
    xlabel('distance(m)');
    ylabel('avgSINR');
    title('Uplink avgSINR & distance')
end


figure(6);
s6 = plot(distancechoice,avgSINR);

sortSINR = zeros(1,number_UE);
sortdistance = zeros(1,number_UE);
%mincount_distance = zeros(1,number_UE);
for ue = 1 : number_UE
    minn = 0;
    for ue2 = 1 : number_UE
        if distancechoice(1,ue) < distancechoice(1,ue2)
            minn = minn + 1;
        end
    end
    %mincount_distance(1,ue) = minn;
    sortdistance(1,number_UE - minn) = distancechoice(1,ue);
    sortSINR(1,number_UE - minn) = avgSINR(1,ue);
end
figure(7);
s7 = plot(sortdistance,sortSINR);
xlabel('Distance (m)');
ylabel('SNR (dB)');
title('SNR & distance')
%}




