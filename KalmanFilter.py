#coding:utf-8
import numpy
import GaussFB
def get_realvalue(originvalue):
    usigma = GaussFB.Gaussfb(originvalue)
    n_iter = len(originvalue)
    sz = (n_iter,)
    
    z = originvalue

    Q = 1e-5 # process variance

    # allocate space for arrays
    xhat=numpy.zeros(sz)      # a posteri estimate of x
    P=numpy.zeros(sz)         # a posteri error estimate
    xhatminus=numpy.zeros(sz) # a priori estimate of x
    Pminus=numpy.zeros(sz)    # a priori error estimate
    K=numpy.zeros(sz)         # gain or blending factor

    R = 0.1**2 # estimate of measurement variance, change to see effect

    # intial guesses
    # xhat[0] = 0.0
    # P[0] = 1.0

    xhat[0] = usigma[0]
    P[0] = usigma[1]

    for k in range(1,n_iter):
        # time update
        xhatminus[k] = xhat[k-1]  #X(k|k-1) = AX(k-1|k-1) + BU(k) + W(k),A=1,BU(k) = 0
        Pminus[k] = P[k-1]+Q      #P(k|k-1) = AP(k-1|k-1)A' + Q(k) ,A=1

        # measurement update
        K[k] = Pminus[k]/( Pminus[k]+R ) #Kg(k)=P(k|k-1)H'/[HP(k|k-1)H' + R],H=1
        xhat[k] = xhatminus[k]+K[k]*(z[k]-xhatminus[k]) #X(k|k) = X(k|k-1) + Kg(k)[Z(k) - HX(k|k-1)], H=1
        P[k] = (1-K[k])*Pminus[k] #P(k|k) = (1 - Kg(k)H)P(k|k-1), H=1
    
    # print('kalman:',xhat[-1])
    return xhat[-1]