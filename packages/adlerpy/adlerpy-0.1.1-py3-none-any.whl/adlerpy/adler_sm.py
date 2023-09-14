import numpy as np
import mpmath as mp
from scipy.interpolate import CubicSpline, PchipInterpolator, Akima1DInterpolator
from scipy.optimize import fsolve

from adlerpy.adler_routines import alphas
from adlerpy.adler_routines import Particle
from adlerpy.adler_routines import adler_massless_connected
from adlerpy.adler_routines import adler_massless_disconnected
from adlerpy.adler_routines import adler_hq_full_zero_loop
from adlerpy.adler_routines import adler_hq_full_one_loop_MS
from adlerpy.adler_routines import adler_hq_full_one_loop_OS
from adlerpy.adler_routines import adler_he_o_heavy_i_massless_Q_supressed_MS
from adlerpy.adler_routines import adler_le_o_heavy_i_massless_m_supressed_MS

from adlerpy.adler_routines import adler_he_o_heavy_i_massless_Q_supressed_OS
from adlerpy.adler_routines import adler_le_o_heavy_i_massless_m_supressed_OS
from adlerpy.adler_routines import adler_o_masless_i_heavy
from adlerpy.adler_routines import adler_db_heavy
from mpmath import zeta
Zeta2=zeta(2);
Zeta3=zeta(3);
Zeta4=zeta(4);
Zeta5=zeta(5);
Zeta7=zeta(7);
alpha0=1/137.035999180;


def adler_charm_pert(aZ,Mz,Q,particles,mpole_on=False,mu=None,nloops=5,mulow=2.4,cut_high_as3=20,cut_low_as3=0.3,QED=False,GG=0):
    """
        Description
        -----------
        
        Computes the conected charm contribution to the adler function at any scale. It relies on the routines given in adler_routines:    
        
        adler_massless_connected
        adler_hq_full_zero_loop
        adler_hq_full_one_loop_MS
        adler_hq_full_one_loop_OS
        adler_he_o_heavy_i_massless_Q_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_OS 
        adler_he_o_heavy_i_massless_Q_supressed_OS
        adler_le_o_heavy_i_massless_m_supressed_OS
        adler_o_masless_i_heavy
        
        When the scale Q is between 2*m*1.5;  2*m*0.7 an spline interpolation is done, since the low and high energy expansions do not converge inside this region.
        
        Parameters
        ----------
        aZ : float.
            Strong coupling constant at Mz. 
        Mz : float.
            Value of the Z mass in GeV.
        Q : float.
            The scale at which the massless Adler function wants to be computed. 
        particles : particles list. 
             List of particles to be included in the theory. This allows to perform the deocupling properly. The charm must be on this list. 
        mpole_on: Bool.
            Tells us if the pole or the MSbar mass is used. 
        mu: float
            Renormalization scale. 
        particles : particles list. 
            List of particles to be included in the theory.This allows to perform the deocupling properly. 
        nloops : int, optional
            The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        mulow: float.
            The lowest value of the renormalization scale allowed. This is to prevent using a divergent value of alphas. At low energies there are only logs of the form log(mu/m) so a too small value is not "natural".
        cut_high_as3: float.
            In case that nloops>2 this parameter tells when to use the higher order large Q tail corrections. The default value is 20. which means that at 20*m the higher order tail corrections are used.
       cut_low_as3: float.
           In case that nloops>2 this parameter tells when to use the higher order low Q tail corrections. The default value is 0.3. which means that at 0.3*m is the  higher order  tail correctiosn are used.
        QED: Bool.
           If true you include terms of order alpha^2
        GG: float
          Value of the gluon condensate in GeV.
        Returns
        ----------
        
        Returns a float.
    
    """
    dQED=0
    dGG=0
    if(QED==True):
        charm=[particle for particle in particles if particle.name=="charm"][0]
        if(charm==None):
            raise TypeError("Did you really added the charm quark?")
        if(mpole_on==None):
            mpole_on=charm.mpole_on
        if(mpole_on):
            m=charm.mpole;
            if(Q<0.001):
                dq0=4/9*adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, m, 4/9*3/4*alpha0, nq=4, k=30, nloops=0)
                dQED=4/9*adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, m, 4/9*3/4*alpha0, nq=4, k=30, nloops=1)-dq0
            else:
                dQED=4/9*(4/9*3/4*alpha0/np.pi*adler_hq_full_one_loop_OS(Q,m))
        else:
            if(charm.mhat["value"]==charm.mhat["scale"]):
                m=charm.mhat["value"]
            else: 
                func = lambda muc : muc - charm.mrun(float(muc),particles=particles,nq=4,aZ=aZ,Mz=Mz) 
                m = fsolve(func,1.27)
            if(Q<0.01):
                dq0=4/9*adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, m, 4/9*3/4*alpha0, nq=4, k=30, nloops=0)
                dQED=4/9*adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, m, 4/9*3/4*alpha0, nq=4, k=30, nloops=1)-dq0
            else:
                dQED=4/9*(4/9*3/4*alpha0/np.pi*adler_hq_full_one_loop_MS(Q,m,m))
    
    if(np.abs(GG)>=0.00001):
        if(QED!=True): 
            charm=[particle for particle in particles if particle.name=="charm"][0]
            if(charm==None):
                raise TypeError("Did you really added the charm quark?")
            if(mpole_on==None):
                mpole_on=charm.mpole_on
            if(mpole_on):
                m=charm.mpole;
            else:
                if(charm.mhat["value"]==charm.mhat["scale"]):
                    m=charm.mhat["value"]
                else: 
                    func = lambda muc : muc - charm.mrun(float(muc),particles=particles,nq=4,aZ=aZ,Mz=Mz) 
                    m = fsolve(func,1.27)
        m2=m**2;
        Q2=Q*Q
        dGG=(2*GG*np.pi**2*(-(np.sqrt(1 + (4*m2)/Q2)*Q2*(2*m2 + Q2)*
              (30*m2**2 + 4*m2*Q2 + Q2**2)) + 
           24*m2**2*(5*m2**2 + 4*m2*Q2 + Q2**2)*
            np.log((2*m2 + Q2 + np.sqrt(1 + (4*m2)/Q2)*Q2)/(2.*m2))))/(np.sqrt(1 + (4*m2)/Q2)*Q2**3*(4*m2 + Q2)**3)
    return adler_charm_pert_QCD(aZ,Mz,Q,particles,mpole_on,mu,nloops,mulow,cut_high_as3,cut_low_as3)+dQED+4/9*dGG
    

def adler_bottom_pert(aZ,Mz,Q,particles,mpole_on=False,mu=None,nloops=5,mulow=2.4,cut_high_as3=20,cut_low_as3=0.3,QED=False,GG=False):
    """
        Description
        -----------
        
        Computes the conected bottom contribution to the adler function at any scale. It relies on the routines given in adler_routines:    
        
        adler_massless_connected
        adler_hq_full_zero_loop
        adler_hq_full_one_loop_MS
        adler_hq_full_one_loop_OS
        adler_he_o_heavy_i_massless_Q_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_OS 
        adler_he_o_heavy_i_massless_Q_supressed_OS
        adler_le_o_heavy_i_massless_m_supressed_OS
        adler_o_masless_i_heavy
        
        When the scale Q is between 2*m*1.5;  2*m*0.75 an spline interpolation is done, since the low and high energy expansions do not converge inside this region.
        
        Parameters
        ----------
        aZ : float.
            Strong coupling constant at Mz. 
        Mz : float.
            Value of the Z mass in GeV.
        Q : float.
            The scale at which the massless Adler function wants to be computed. 
        particles : particles list. 
             List of particles to be included in the theory. This allows to perform the deocupling properly. The charm must be on this list. 
        mpole_on: Bool.
            Tells us if the pole or the MSbar mass is used. 
        mu: float
            Renormalization scale. 
        particles : particles list. 
            List of particles to be included in the theory.This allows to perform the deocupling properly. 
        nloops : int, optional
            The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        mulow: float.
            The lowest value of the renormalization scale allowed. This is to prevent using a divergent value of alphas. Ar low energies,
            there are only logs of the form log(mu/m) so a too small value is not "natural".
        cut_high_as3: float.
            In case that nloops>2 this parameter tells when to use the higher order large Q tail corrections. The default value is 20. which means that at 20*m the higher order tail corrections are used.
       cut_low_as3: float.
           In case that nloops>2 this parameter tells when to use the higher order low Q tail corrections. The default value is 0.3. which means that at 0.3*m is the  higher order  tail correctiosn are used.
        QED: Bool.
           If true you include terms of order alpha^2
        GG: float
          Value of the gluon condensate in GeV.
        Returns
        ----------
        
        Returns an array where the first component is the QCD and the second the QEd term
    
    """
    dQED=0
    
    if(QED==True):
        bottom=[particle for particle in particles if particle.name=="bottom"][0]
        if(bottom==None):
            raise TypeError("Did you really added the charm quark?")
        if(mpole_on==None):
            mpole_on=bottom.mpole_on
        if(mpole_on):
            m=bottom.mpole;
            if(Q<0.01):
                dq0=1/9*adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, m, 1/9*3/4*alpha0, nq=5, k=30, nloops=0)
                dQED=1/9*adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, m, 1/9*3/4*alpha0, nq=5, k=30, nloops=1)-dq0
            else:
                dQED=1/9*(1/9*3/4*alpha0/np.pi*adler_hq_full_one_loop_OS(Q,m))
        else:
            if(bottom.mhat["value"]==bottom.mhat["scale"]):
                m=bottom.mhat["value"]
            else: 
                func = lambda mub : mub - charm.mrun(float(mub),particles=particles,nq=5,aZ=aZ,Mz=Mz) 
                m = fsolve(func,4.18)
            if(Q<0.01):
                dq0=1/9*adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, m, 1/9*3/4*alpha0, nq=5, k=30, nloops=0)
                dQED=1/9*adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, m, 1/9*3/4*alpha0, nq=5, k=30, nloops=1)-dq0
            else:
                dQED=1/9*(1/9*3/4*alpha0/np.pi*adler_hq_full_one_loop_MS(Q,m,m))
    if(GG!=False or np.abs(GG)<0.0001): #Condensates
        bottom=[particle for particle in particles if particle.name=="bottom"][0]
        if(bottom==None):
            raise TypeError("Did you really added the charm quark?")
        if(mpole_on==None):
            mpole_on=bottom.mpole_on
        if(mpole_on):
            m=bottom.mpole;
        else:
            if(bottom.mhat["value"]==bottom.mhat["scale"]):
                m=bottom.mhat["value"]
            else: 
                func = lambda mub : mub - bottom.mrun(float(muc),particles=particles,nq=5,aZ=aZ,Mz=Mz) 
                m = fsolve(func,4.18)
        m2=m**2;
        Q2=Q**2;
        if(Q2<0.1*m2):
            dGG=GG*((-0.5639773943479633*Q2)/m2**3 + (0.4699811619566361*Q2**2)/m2**4 - 
       (0.2563533610672561*Q2**3)/m2**5 + (0.11503035432505081*Q2**4)/m2**6 - 
       (0.046012141730020314*Q2**5)/m2**7 + (0.017051558405831058*Q2**6)/m2**8)
        else:
            dGG=GG*(2*np.pi**2*(-(Q2*(2*m2 + Q2)*(30*m2**2 + 4*m2*Q2 + Q2**2)) + (24*m2**2*(5*m2**2 + 4*m2*Q2 + Q2**2)*
              np.log((2*m2 + Q2 + np.sqrt(1 + (4*m2)/Q2)*Q2)/(2.*m2)))/np.sqrt(1 + (4*m2)/Q2)))/(Q2**3*(4*m2 + Q2)**3)
    return adler_bottom_pert_QCD(aZ,Mz,Q,particles,mpole_on,mu,nloops,mulow,cut_high_as3,cut_low_as3)+dQED+1/9*dGG
    



def adler_charm_pert_QCD(aZ,Mz,Q,particles,mpole_on=False,mu=None,nloops=5,mulow=2.4,cut_high_as3=20,cut_low_as3=0.3):
    """
        Description
        -----------
        
        Computes the conected charm contribution to the adler function at any scale. It relies on the routines given in adler_routines:    
        
        adler_massless_connected
        adler_hq_full_zero_loop
        adler_hq_full_one_loop_MS
        adler_hq_full_one_loop_OS
        adler_he_o_heavy_i_massless_Q_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_OS 
        adler_he_o_heavy_i_massless_Q_supressed_OS
        adler_le_o_heavy_i_massless_m_supressed_OS
        adler_o_masless_i_heavy
        
        When the scale Q is between 2*m*1.5;  2*m*0.7 an spline interpolation is done, since the low and high energy expansions do not converge inside this region.
        
        Parameters
        ----------
        aZ : float.
            Strong coupling constant at Mz. 
        Mz : float.
            Value of the Z mass in GeV.
        Q : float.
            The scale at which the massless Adler function wants to be computed. 
        particles : particles list. 
             List of particles to be included in the theory. This allows to perform the deocupling properly. The charm must be on this list. 
        mpole_on: Bool.
            Tells us if the pole or the MSbar mass is used. 
        mu: float
            Renormalization scale. 
        particles : particles list. 
            List of particles to be included in the theory.This allows to perform the deocupling properly. 
        nloops : int, optional
            The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        mulow: float.
            The lowest value of the renormalization scale allowed. This is to prevent using a divergent value of alphas. Ar low energies,
            there are only logs of the form log(mu/m) so a too small value is not "natural".
        cut_high_as3: float.
            In case that nloops>2 this parameter tells when to use the higher order large Q tail corrections. The default value is 20. which means that at 20*m the higher order tail corrections are used.
       cut_low_as3: float.
           In case that nloops>2 this parameter tells when to use the higher order low Q tail corrections. The default value is 0.3. which means that at 0.3*m is the  higher order  tail correctiosn are used.
        Returns
        ----------
        
        Returns a float.
    
    """
    cut_high=1.5;
    cut_low=0.7;
    if(mu==None):
        mu=float(Q); 
        mu0=None;
    else:
        mu0=mu
    
    #Look up for the charm in your list of particles
    charm=[particle for particle in particles if particle.name=="charm"][0]
    if(charm==None):
        raise TypeError("Did you really added the charm quark?")
    
    #Check consistency between mu and Q
    particles_sorted = sorted(particles, key=lambda x: x.mudec)
    nq=int(sum(map(lambda particle : particle.mudec<mu,particles_sorted )))
    #nqQ=sum(map(lambda particle : particle.mudec<Q,particles_sorted )) 
   # if(nqQ!=nqmu):
   #     raise TypeError("The nq corresponding to such mu does not correspond to the nq for q, this may lead to inconsistencies. Please change your mu")
    if(nq<4):nq=4;
    #else:nq=nqQ
    if(mu<mulow):mu=mulow;
    asmu=alphas(aZ, Mz, mu, particles,nq=nq);
    
    #Check if pole or ms mass is used we allow to choose also within the function. 
    if(mpole_on==None):
        mpole_on=charm.mpole_on
    if(mpole_on):
        m=charm.mpole;
        if(nloops==0):
            return 4/9*adler_hq_full_zero_loop(Q,m)
        if(nloops==1):
            if(Q<0.05):
                return 4/9*adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)
            else:
                return 4/9*(adler_hq_full_zero_loop(Q,m)+asmu/np.pi*adler_hq_full_one_loop_OS(Q,m))
        
        if(nloops>1):
            try:
                  bottom=[particle for particle in particles if particle.name=="bottom"][0]
            except:
                  TypeError("To compute the double bubble mass supresed terms coming from the bottom quark, I need the bottom quark. Did you really added the bottom quark?")
            if(bottom.mpole_on==True):
                mb=bottom.mpole
            else:
                if(nq<5):
                     nqbottom=5;
                mb=bottom.mrun(float(mu),particles=particles,nq=5,aZ=aZ,Mz=Mz)
            double_bubble=(asmu/np.pi)**2*adler_db_heavy(Q,m,mb,cut_low,cut_high)
            if(Q<2*m*cut_low):
                if(Q<cut_low_as3*m):
                    return  4/9*(adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)+double_bubble)
                else:
                    return  4/9*(adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=2)+double_bubble)
                    
            if(Q>2*m*cut_high):
                if(Q>cut_high_as3*m):
                    return 4/9*(adler_he_o_heavy_i_massless_Q_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=nloops)+double_bubble)
                else:
                    return 4/9*(adler_he_o_heavy_i_massless_Q_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=2)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=2)+double_bubble)
        
        #If the code reaches this point, interpolation will be needed.
        
        x=[2*m*cut_low*0.70,    2*m*cut_low*0.80,  2*m*cut_low*0.90, 2*m*cut_low*0.98,   
           2*m*cut_high*1.05,   2*m*cut_high*1.15, 2*m*cut_high*1.25, 2*m*cut_high*1.35]
        #mus=[max(x[0],mulow),max(x[1],mulow),max(x[2],mulow),max(x[3],mulow),
        #     x[4],x[5],x[6],x[7]]
        y=[]
        for i in range(len(x)):
            y.append(adler_charm_pert_QCD(aZ,Mz,x[i],particles,mpole_on=mpole_on,mu=mu0,nloops=nloops,mulow=mulow))
        spl = CubicSpline(x,y)
        return spl(Q)
   
    else:
        
        m=charm.mrun(float(mu),particles=particles,nq=nq,aZ=aZ,Mz=Mz)
        if(nloops==0):
            return 4/9*adler_hq_full_zero_loop(Q,m)
        if(nloops==1):
            if(Q<0.05):
                return 4/9*adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)
            else:
                return 4/9*(adler_hq_full_zero_loop(Q,m)+asmu/np.pi*adler_hq_full_one_loop_MS(Q,m,mu))
           
        if(nloops>1):
            try:
                  bottom=[particle for particle in particles if particle.name=="bottom"][0]
            except:
                  TypeError("To compute the double bubble mass supresed terms coming from the bottom quark, I need the bottom quark. Did you really added it?")
            if(bottom.mpole_on==True):
                mb=bottom.mpole
            else:
                if(nq<5):
                     nqbottom=5;
                mb=bottom.mrun(float(mu),particles=particles,nq=5,aZ=aZ,Mz=Mz)
            double_bubble=(asmu/np.pi)**2*adler_db_heavy(Q,m,mb,cut_low,cut_high)
            mcut=m
            if(Q<2*mcut*cut_low):
                if(Q<mcut*cut_low_as3):
                    return  4/9*(adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)+double_bubble)
                else:
                    return  4/9*(adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=2)+double_bubble)
            if(Q>2*mcut*cut_high):
                if(Q>cut_high_as3*mcut):
                    return 4/9*(adler_he_o_heavy_i_massless_Q_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=nloops)+double_bubble)
                else:
                    return 4/9*(adler_he_o_heavy_i_massless_Q_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=2)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=2)+double_bubble)
             
       #If the code reaches this point, interpolation will be needed.
        x=[2*m*cut_low*0.70,    2*m*cut_low*0.80,  2*m*cut_low*0.90, 2*m*cut_low*0.999,   
           2*m*cut_high*1.0001,   2*m*cut_high*1.15, 2*m*cut_high*1.25, 2*m*cut_high*1.35]
        #mus=[max(x[0],mulow),max(x[1],mulow),max(x[2],mulow),max(x[3],mulow),
        #     x[4],x[5],x[6],x[7]]
        y=[]
        for i in range(len(x)):
            try:
                y.append(adler_charm_pert_QCD(aZ,Mz,x[i],particles,mpole_on=mpole_on,mu=mu0,nloops=nloops,mulow=mulow))
            except: 
                raise TypeError("this mu=",x[i])

        spl = CubicSpline(x,y)
        return spl(Q)
        

def adler_bottom_pert_QCD(aZ,Mz,Q,particles,mpole_on=False,mu=None,nloops=5,mulow=2.4,cut_high_as3=20,cut_low_as3=0.3):
    """
        Description
        -----------
        
        Computes the conected bottom contribution to the adler function at any scale. It relies on the routines given in adler_routines:    
        
        adler_massless_connected
        adler_hq_full_zero_loop
        adler_hq_full_one_loop_MS
        adler_hq_full_one_loop_OS
        adler_he_o_heavy_i_massless_Q_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_MS
        adler_le_o_heavy_i_massless_m_supressed_OS 
        adler_he_o_heavy_i_massless_Q_supressed_OS
        adler_le_o_heavy_i_massless_m_supressed_OS
        adler_o_masless_i_heavy
        
        When the scale Q is between 2*m*1.5;  2*m*0.75 an spline interpolation is done, since the low and high energy expansions do not converge.
        
        Parameters
        ----------
        aZ : float.
            Strong coupling constant at Mz. 
        Mz : float.
            Value of the Z mass in GeV.
        Q : float.
            The scale at which the massless Adler function wants to be computed. 
        particles : particles list. 
             List of particles to be included in the theory. This allows to perform the deocupling properly. The charm must be on this list. 
        mpole_on: Bool.
            Tells us if the pole or the MSbar mass is used. 
        mu: float
            Renormalization scale. 
        particles : particles list. 
            List of particles to be included in the theory.This allows to perform the deocupling properly. 
        nloops : int, optional
            The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        mulow: float.
            The lowest value of the renormalization scale allowed. This is to prevent using a divergent value of alphas. Ar low energies,
            there are only logs of the form log(mu/m) so a too small value is not "natural".
        cut_high_as3: float.
            In case that nloops>2 this parameter tells when to use the higher order large Q tail corrections. The default value is 20. which means that at 20*m the higher order tail corrections are used.
       cut_low_as3: float.
           In case that nloops>2 this parameter tells when to use the higher order low Q tail corrections. The default value is 0.3. which means that at 0.3*m is the  higher order  tail correctiosn are used.
        
        Returns
        ----------
        
        Returns a float.
    
    """
    cut_high=1.5;
    cut_low=0.75;
    if(mu==None):
        mu=float(Q); 
        mu0=None;
    else:
        mu0=mu
    
    #Look up for the charm in your list of particles
    bottom=[particle for particle in particles if particle.name=="bottom"][0]
    if(bottom==None):
        raise TypeError("Did you really added the bottom quark?")
    
    #Check consistency between mu and Q
    particles_sorted = sorted(particles, key=lambda x: x.mudec)
    nq=sum(map(lambda particle : particle.mudec<mu,particles_sorted )) 
    if(nq<5):nq=5;
    if(mu<mulow):mu=mulow;
    asmu=alphas(aZ, Mz, mu, particles,nq=nq);
    #Check if pole or ms mass is used we allow to choose also within the function. 
    if(mpole_on==None):
        mpole_on=bottom.mpole_on
    if(mpole_on):
        m=bottom.mpole;
       
        if(nloops==0):
            return 1/9*adler_hq_full_zero_loop(Q,m)
        if(nloops==1):
            if(Q<0.05):
                return 1/9*adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)
            else:
                return 1/9*(adler_hq_full_zero_loop(Q,m)+asmu/np.pi*adler_hq_full_one_loop_OS(Q,m))
        
        if(nloops>1):
            if(Q<2*m*cut_low):
                if(Q<cut_low_as3*m):
                    return  1/9*(adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops))
                else:
                    return  1/9*(adler_le_o_heavy_i_massless_m_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=2))
                    
            if(Q>2*m*cut_high):
                if(Q>cut_high_as3*m):
                    return 1/9*(adler_he_o_heavy_i_massless_Q_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=nloops))
                else:
                    return 1/9*(adler_he_o_heavy_i_massless_Q_supressed_OS(m, Q, mu, asmu, nq=nq, k=30, nloops=2)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=2))
        
        #If the code reaches this point, interpolation will be needed.
        
        x=[2*m*cut_low*0.70,    2*m*cut_low*0.80,  2*m*cut_low*0.90, 2*m*cut_low*0.98,   
           2*m*cut_high*1.05,   2*m*cut_high*1.15, 2*m*cut_high*1.25, 2*m*cut_high*1.35]
        y=[]
        for i in range(len(x)):
            y.append(adler_bottom_pert_QCD(aZ,Mz,x[i],particles,mpole_on=mpole_on,mu=mu0,nloops=nloops,mulow=mulow))
        spl = CubicSpline(x,y)
        return spl(Q)
   
    else:
        m=bottom.mrun(float(mu),particles=particles,nq=nq,aZ=aZ,Mz=Mz)
        if(nloops==0):
            return 1/9*adler_hq_full_zero_loop(Q,m)
        if(nloops==1):
            if(Q<0.001):
                return 1/9*adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)
            else:
                return 1/9*(adler_hq_full_zero_loop(Q,m)+asmu/np.pi*adler_hq_full_one_loop_MS(Q,m,mu))
        if(nloops>1):
            if(Q<2*m*cut_low):
                if(Q<m*cut_low_as3):
                    return  1/9*(adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops))
                else:
                    return  1/9*(adler_le_o_heavy_i_massless_m_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=2))
            if(Q>2*m*cut_high):
                if(Q>cut_high_as3*m):
                    return 1/9*(adler_he_o_heavy_i_massless_Q_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=nloops)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=nloops))
                else:
                    return 1/9*(adler_he_o_heavy_i_massless_Q_supressed_MS(m, Q, mu, asmu, nq=nq, k=30, nloops=2)+
                           adler_massless_connected(Q, mu, asmu, nq=nq, nloops=2))
             
       #If the code reaches this point, interpolation will be needed.
        
        x=[2*m*cut_low*0.70,    2*m*cut_low*0.80,  2*m*cut_low*0.90, 2*m*cut_low*0.98,   
           2*m*cut_high*1.05,   2*m*cut_high*1.15, 2*m*cut_high*1.25, 2*m*cut_high*1.35]
        y=[]
        for i in range(len(x)):
            y.append(adler_bottom_pert_QCD(aZ,Mz,x[i],particles,mpole_on=mpole_on,mu=mu0,nloops=nloops,mulow=mulow))
        spl = CubicSpline(x,y)
        return spl(Q)

def adler_light_pert(aZ,Mz,Q,particles,mu=None,nloops=5,QED=False,GG=0,qq=0):
    """
        Description
        -----------
        
        Computes the conected uds contribution to the adler function at any scale. It relies on the routines given in adler_routines:    
        
        adler_massless_connected
        adler_he_o_heavy_i_massless_Q_supressed_MS
        adler_o_masless_i_heavy
        
     
        Parameters
        ----------
        aZ : float.
            Strong coupling constant at Mz. 
        Mz : float.
            Value of the Z mass in GeV.
        Q : float.
            The scale at which the massless Adler function wants to be computed. 
        particles : particles list. 
             List of particles to be included in the theory. This allows to perform the deocupling properly. The charm must be on this list.   
        mu: float
            Renormalization scale. 
        nloops : int, optional
            The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        QED: Bool.
           If true you include terms of order alpha^2
        GG: float
          Value of the gluon condensate in GeV.
        qq: float
          Value of the quark condensate in GeV.
        Returns
        ----------
        
        Returns a float.
    
    """
    if(mu==None):mu=float(Q);
    
    
    #Check consistency between mu and Q
    particles_sorted = sorted(particles, key=lambda x: x.mudec)
    nqmu=sum(map(lambda particle : particle.mudec<mu,particles_sorted )) 
    nqQ=sum(map(lambda particle : particle.mudec<Q,particles_sorted )) 
    if(nqQ!=nqmu):
        raise TypeError("The nq corresponding to such mu does not correspond to the nq for q, this may lead to inconsistencies. Please change your mu")
    nq=int(nqmu)
    asmu=alphas(aZ, Mz, mu, particles,nq=nq);
    strange=[particle for particle in particles if particle.name=="strange"][0]
    if(strange==None):
        raise TypeError("Did you really added the strange quark?")
    ms=strange.mrun(float(mu),particles=particles,nq=nq,aZ=aZ,Mz=Mz)   
    ad_msQ=adler_he_o_heavy_i_massless_Q_supressed_MS(ms,Q,mu,asmu,nq,k=15,nloops=nloops)
    double_bubble=0
    if(nloops>1):
            try:
                bottom=[particle for particle in particles if particle.name=="bottom"][0]
                charm=[particle for particle in particles if particle.name=="charm"][0]
            except:
                  TypeError("To compute the double bubble mass supresed terms coming from the bottom and charm quark. Did you really added them?")
            if(bottom.mpole_on==True):
                mb=bottom.mpole
            else:
                mb=bottom.mrun(float(mu),particles=particles,nq=5,aZ=aZ,Mz=Mz)
            if(charm.mpole_on==True):
                mc=charm.mpole
            else:
                mc=charm.mrun(float(mu),particles=particles,nq=4,aZ=aZ,Mz=Mz)
                
            double_bubble=(asmu/np.pi)**2*(adler_o_masless_i_heavy(mc,Q,cut=charm.mudec)+ adler_o_masless_i_heavy(mb,Q,cut=bottom.mudec))
    condensates=4*np.pi**2/3/Q**4*((1+7/6*asmu/np.pi)*GG+4*(1+asmu/3/np.pi+(27/8+4*Zeta3)*(asmu/np.pi)**2)*qq)
    return 2/3*adler_massless_connected(Q,mu,asmu,nq,nloops=nloops)+1/9*ad_msQ+2/3*double_bubble+condensates


def adler_OZI_pert(aZ,Mz,Q,particles,mu=None,nloops=5,QED=False,GG=0,qq=0):
    """
        Description
        -----------
        
        Computes the disconnected contribution to the adler function at any scale (uses mass-less expressions). It relies on the routines given in adler_routines:    
        
        adler_massless_disconnected
        
     
        Parameters
        ----------
        aZ : float.
            Strong coupling constant at Mz. 
        Mz : float.
            Value of the Z mass in GeV.
        Q : float.
            The scale at which the massless Adler function wants to be computed. 
        particles : particles list. 
             List of particles to be included in the theory. This allows to perform the deocupling properly. The charm must be on this list.   
        mu: float
            Renormalization scale. 
        nloops : int, optional
            The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        QED: Bool.
           If true you include terms of order alpha^2
        GG: float
          Value of the gluon condensate in GeV. Still not fully implemented.
        qq: float
          Value of the quark condensate in GeV. Still not fully implemented.
        Returns
        ----------
        
        Returns a float.
    
    """
    particles_sorted = sorted(particles, key=lambda x: x.mudec)
    if(mu==None):
        mu=Q;
    nq=sum(map(lambda particle : particle.mudec<mu,particles_sorted )) 
    asmu=alphas(aZ, Mz, mu, particles,nq=nq);
    Qozi=[0,(2/3),1/3,0,2/3,1/3,1]
    return  Qozi[nq]**2*adler_massless_disconnected(Q,mu,asmu,nq,nloops=nloops)