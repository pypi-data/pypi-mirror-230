################################################################################
# File: Adler
# Date: 14.08.2023
# Author: Rodolfo F

# Description: This code computes the different components of the  Adler function.

################################################################################



import rundec
import numpy as np
import mpmath as mp
from mpmath import polylog
from mpmath import zeta
crd = rundec.CRunDec()

Zeta2=zeta(2);
Zeta3=zeta(3);
Zeta4=zeta(4);
Zeta5=zeta(5);
Zeta7=zeta(7);



class Particle:
	"""
    A class used to represent a Particle.
    ...

    Attributes
    ----------
	name : str
		The name of the particle to be used. For example "charm".
	mhat : dict
		{"value":x[0],"scale":x[1],"nq":x[2]}. The first element "value" is a float which contains the value of the mass.
		The second is a float which contains the scale at which such mass is evaluated. 
		The last is the number of quarks under which this mass is evaluated.
		For heavy quarks please use nq=4 for the charm and nq=5 for the bottom.  When creating it, just give as input a  list of floats x. 
		
    mpole : float
			Pole mass of the heavy quark. The default value is none.  
		
		mudec : float
			Scale at which we want to decouple  this particle.   
		
		mpole_on: Bool
			It determines if the pole or the MS mass is used. If mpole=True, everything will be calculated using pole mass relations.
	"""
	

	def __init__(self, name,x={0,0,0},mudec=None,mpole=None,mpole_on=False):
		"""
		 Attributes
		----------
		name : str
		The name of the particle to be used. For example "charm".
		mhat : dict
			{"value":x[0],"scale":x[1],"nq":x[2]}. The first element "value" is a float which contains the value of the mass.
			The second is a float which contains the scale at which such mass is evaluated. 
			The last is the number of quarks under which this mass is evaluated.
			For heavy quarks please use nq=4 for the charm and nq=5 for the bottom.  When creating it, just give as input a  list of floats x. 
		
		mpole : float
			Pole mass of the heavy quark. The default value is none.  
		
		mudec : float
			Scale at which we want to decouple this particle.  
		
		mpole_on: Bool
			It determines if the pole or the MS mass is used. If mpole=True, everything will be calculated using pole mass relations.
		
		"""
		self.name=name
		self.mhat={"value":x[0],"scale":x[1],"nq":x[2]} 
		self.mpole=mpole
		self.mpole_on=mpole_on;
		self.mudec=mudec;
	
	def mrun(self,mu,particles,aZ,Mz,nq=None,nloops=5):
		"""
        Description
        -----------
        
        Returns the value of the MSbar mass at an arbitrary scale, with an arbitrary number of quarks. I rely on the rundec code which can be obtained in https://github.com/DavidMStraub/rundec-python
        
        Parameters
        ----------
        
		mu : float
			Renormalization scale. 
		particles : particles list. 
			List of particles to be included in the theory.This allows to perform the deocupling properly.
		aZ: float
			Value of alphas at the M_Z scale.
		Mz: float
			Value of the Mz mass. 
		nq: int
			number of active quarks. When none, it takes the decoupling scales given in the list of particles. 
        nloops : int, optional
			The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        
		Returns
        ----------
        
		It returns a float. 
 
    """
		n_input=self.mhat["nq"];
		mu0=self.mhat["scale"]
		m=self.mhat["value"]
		particles_sorted = sorted(particles, key=lambda x: x.mudec)
		n_mu_pos=sum(map(lambda particle : particle.mudec<mu,particles_sorted))
		n_part_pos=sum(map(lambda particle : particle.mudec<self.mudec+0.0000001,particles_sorted))
		if(nq==None):nq=n_mu_pos;
		nq=int(nq);
		if(nq>6):
			raise TypeError("Not implemented for more than 6 quarks yet :(")
		if(nq<n_part_pos):
			raise TypeError("Check your input quark mass for the "+self.name+" quark")
		if(nq>=n_input): up=1;
		else:up=-1;
		nf=n_input
		while(nf!=nq):
			amu0=alphas(aZ,Mz,mu0,particles_sorted,nq=nf,nloops=nloops);
			mudec_next=particles_sorted[nf-1+up].mudec
			amu1=alphas(aZ,Mz,mudec_next,particles_sorted,nq=nf,nloops=nloops);
			m_mu=crd.mMS2mMS(m,amu0,amu1,nf,nloops)
			if(up==1):
				m=crd.DecMqUpMS(m_mu, amu1, mudec_next, mudec_next,nf, nloops)
			else:
				m=crd.DecMqDownMS(m_mu, amu1, mudec_next, mudec_next,nf-1, nloops)
			nf+=up;
			mu0=mudec_next
		amu0=alphas(aZ,Mz,mu0,particles_sorted,nq=nq,nloops=nloops);
		amu1=alphas(aZ,Mz,mu,particles_sorted,nq=nq,nloops=nloops);
		return crd.mMS2mMS(m,amu0,amu1,nq,nloops)







def alphas(aZ,Mz,mu,particles,nq=None,nloops=5):
	"""
        Description
        -----------
        
        Strong coupling constant at scale mu.  I rely on the rundec code which can be obtained in https://github.com/DavidMStraub/rundec-python.
        
        Parameters
        ----------
        
        aZ : float.
            Strong coupling constant at Mz. 
		Mz : float.
            Value of the Z mass in GeV.
        mu: float
            Renormalization scale. 
        particles : particles list. 
			List of particles to be included in the theory.This allows to perform the deocupling properly. 
        nq: int
			number of active quarks. When none, it takes the decoupling scales given in the list of particles. 
        nloops : int, optional
			The number of loops at which the RGE is to be evaluated. nloops=5 is the default value.
        Returns
        ----------
        
        Returns a float.
        
    """
	if(nloops==0):
		return aZ
	particles_sorted = sorted(particles, key=lambda x: x.mudec)
	if(nq==None):
		nq=int(sum(map(lambda particle : particle.mudec<mu,particles)))
	nq=int(nq);
	if(nq==5):
		return crd.AlphasExact(aZ,Mz,mu,5,nloops)
	if(nq>6):
		raise TypeError("Not implemented for more than 6 quarks yet :(")
	if(nq==6):
		mu_dec=particles_sorted[5].mudec;
		if(particles_sorted[5].mpole_on==True):
			mtop=particles_sorted[5].mpole;
			asdown=crd.AlphasExact(aZ,Mz,mu_dec,5,nloops)
			asup=crd.DecAsUpOS(asdown,mtop,mu_dec,5,nloops)
		else:
			mtop=particles_sorted[5].mhat["value"];
			if(mtop!=particles_sorted[5].mhat["scale"]):
				raise TypeError("Give mt(mt) as input")
			asdown=crd.AlphasExact(aZ,Mz,mtop,5,nloops)
			asup=crd.DecAsUpMS(asdown,mtop,mu_dec,5,nloops)
		return crd.AlphasExact(asup,mu_dec,mu,6,nloops) 
	ni=5
	mu0=Mz;
	as_mu0=aZ;
	while(ni!=nq):
		mu_dec=particles_sorted[ni-1].mudec;
		as_mudec_up=crd.AlphasExact(as_mu0,mu0,mu_dec,ni,nloops)#------------α(mu_dec)+
		if(particles_sorted[ni-1].mpole_on==False):
			mhat_mu_input=particles_sorted[ni-1].mhat["value"];
			mu_input=particles_sorted[ni-1].mhat["scale"];
			if(particles_sorted[ni-1].mhat["nq"]>ni):
				raise TypeError("Correct nq for "+particles_sorted[ni-1].name +"\n"+"Please be aware that for the heavy quarks, one most use an input value consistent with the"+"\n"+"position of the particle relative to the other particles. For example, for the charm quark use a value of m with nq=4")
			as_muinput_up=crd.AlphasExact(as_mu0,mu0,mu_input,ni,nloops) #------------α(mu_input)+
			mhat_mudec=crd.mMS2mMS(mhat_mu_input,as_muinput_up,as_mudec_up,ni,nloops)#------------m(mu_dec)
			as_mudec_down=crd.DecAsDownMS(as_mudec_up,mhat_mudec,mu_dec,ni-1,nloops)
		else:
			mpole=particles_sorted[ni-1].mpole;
			as_mudec_down=crd.DecAsDownOS(as_mudec_up,mpole,mu_dec,ni-1,nloops)
		ni-=1
		mu0=mu_dec
		as_mu0=as_mudec_down
	return   crd.AlphasExact(as_mudec_down,mu_dec,mu,ni,nloops) 

   



# ADLER function routines. 


def adler_massless_connected(Q,mu,asmu,nq,nloops=4):
    """
        Description
        -----------
        
        Connected and massless contribution to the Adler function. It can either be obtained from the massless expression of R given in 
        https://arxiv.org/abs/1501.06739 or from the QED RGE results given in https://arxiv.org/pdf/1206.1284.pdf.  
        
        Parameters
        ----------
        
        Q : float or mp complex number.
            The scale at which the massless Adler function wants to be computed. 
        mu : float
            Renormalization scale. 
        asmu : float
            Strong coupling constant at scale mu. 
        nloops : int, optional
            The number of loops at which the Adler function is to be evaluated. nloops=5 is the default value which includes 
            the terms up to order asmu**4;
        
        Returns
        ----------
        
        If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges.     
        
    
    """
        
    L=mp.log(Q**2/mu**2);
    if(nloops>5):
        raise TypeError("Massless connected Adler function not available at order $alphas_s^5$")
    a=asmu/np.pi
    d=[1,
          1,
          15.208333333333334 - (11*L)/4. - (11*nq)/12. + (L*nq)/6. - 11*Zeta3 + 
          (2*nq*Zeta3)/3.,
       
          18.242692175590775 - 17.296390692177879*L + 7.5625*L**2 + 
          (-4.2158465093448754 + 2.0876938212740864*L - 0.91666666666666667*L**2)*nq + 
          (0.086206870616087972 - 0.038431799297867937*L + 0.027777777777777778*L**2)*nq**2,
       
          135.79162363984509 - 198.1402922804908*L + 88.878861605233751*L**2 - 
          20.796875*L**3 + (-34.440227260541445 + 52.885056438560013*L - 
          16.175418019133409*L**2 + 3.78125*L**3)*nq + 
          (1.8752514772549715 - 3.095720335771888*L + 0.81239907186667127*L**2 - 
          0.22916666666666667*L**3)*nq**2 + 
          (-0.010092783354352401 + 0.043103435308043986*L - 0.0096079498244669841*L**2 + 
          0.0046296296296296296*L**3)*nq**3];
    
    powers = np.arange(len(d[0:nloops+1]))
    terms = d[0:nloops+1] * (a ** powers)
    return 3*np.sum(terms)


def adler_massless_disconnected(Q,mu,asmu,nq,nloops=5):
    """
        Description
        -----------
        
        Disconnected and masseless contribution to the Adler function. It can either be obtained from the massless expression of R given in 
        https://arxiv.org/abs/1501.06739 or from the QED RGE results given in https://arxiv.org/pdf/1206.1284.pdf.  
        
        Parameters
        ----------
        
        Q : float or mp complex number.
            The scale at which the massless Adler function wants to be computed. 
        mu : float
            Renormalization scale. 
        asmu : float
            Strong coupling constant at scale mu. 
        nloops : int, optional
            The number of loops at which the Adler function is to be evaluated. nloops=5 is the default value which includes 
            the terms up to order asmu**4;
        
        Returns
        ----------
        
        If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges.     
        
    
    """
    L=mp.log(Q**2/mu**2);
    if(nloops>5):
        raise TypeError("Massless disconnected Adler function not available at order $alphas_s^5$")
    a=asmu/np.pi
    d=[0,
          0,
          0,
        -1.2395392830437682534,
        (-17.826737020065351267 + 10.226199085111088091*L)+
        (0.5748849178328720010 - 0.6197696415218841267*L)*nq];
    
    powers = np.arange(len(d[0:nloops+1]))
    terms = d[0:nloops+1] * (a ** powers)
    return 3*np.sum(terms)
 

def adler_hq_full_zero_loop(Q,m):
	"""
		Description
		-----------
		Full expression for the Adler function at order $\alpha^{0}_s$. 
		
		Parameters
		----------
		Q : float or mp complex number.
			The scale at which the Adler function wants to be computed. 
		m : float
		Mass of the particle. At this order it can be either the pole or the MSbar mass.  
		
		Returns
		----------
		If complex number was used as input, returns a complex number. If positive real, returns a real number. 
		IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges.     
	"""
	Q2=Q**2;
	return 3 - (18*m**2)/Q2 - (36*m**4*mp.log((2*m**2 + Q2 - mp.sqrt(1 + (4*m**2)/Q2)*Q2)/(2.*m**2)))/(mp.sqrt(1 + (4*m**2)/Q2)*Q2**2)





def adler_hq_full_one_loop_MS(Q,mhat,mu):
	"""
		Description
		-----------
		Full contribution of to the Adler function at order $\alpha^{1}_s$ in the Msbar scheme. 
		
		Parameters
		----------
		Q : float or mp complex number.
			The scale at which the  Adler function wants to be computed. 
		mhat : float
			Msbar mass of the particle at scale mu. 
		mu : float
			Renormalization scale.
		Returns
		----------
		If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges and bu $\hat{\alpha}_s/pi$.     
	"""
	Q2=Q**2;
	m=mhat;
	m2=m**2;
	m4=m**4;
	Q4=Q2**2;
	Q6=Q2**3;
	u=(2*m2 + Q2 - mp.sqrt(1 + (4*m2)/Q2)*Q2)/(2.*m2);
	v=mp.sqrt(1 + (4*m2)/Q2)
	Lu=mp.log(u)
	t=4*m2 + Q2
	return (
		(Q2*(-44*m2 + 3*Q2) - (12*m2*(9*m2 + Q2)*Lu)/mp.sqrt(1 + (4*m2)/Q2))/Q4 - 
    (4*m2*Lu*(m2 + 4*Q2 + (m2 + 2*Q2)*v*Lu))/(mp.sqrt(1 + (4*m2)/Q2)*Q4) + 
    (12*(4 + 3*mp.log(mu**2/m2))*(m2*Q2*(6*m2 + Q2)*(2*m2*(-2 + v) + Q2*(-1 + v)) + 
    4*m4*(3*m2 + Q2)*(2*m2 + Q2 - Q2*v)*Lu))/(mp.sqrt(1 + (4*m2)/Q2)*Q4*t*(-2*m2 + Q2*(-1 + v))) + 
    (4*m2*(Lu*(4*Q2*(-2*m2 + Q2)*v*mp.log(2/(1 + v)) + 8*Q2*(-2*m2 + Q2)*v*mp.log((t - Q2*v)/(2.*m2)) + 
               Lu*(-((2*m2 - Q2)*(4*m2 - 3*Q2*(-1 + v))) + 
                  2*(16*m4 - Q4)*(mp.log(1/(2 + 2*v)) + 2*mp.log(4 + (Q2 - Q2*v)/m2)))) + 
            4*(Q2*(-2*m2 + Q2)*v + (32*m4 - 2*Q4)*Lu)*polylog(2,u) + 
            8*(Q2*(-2*m2 + Q2)*v + (32*m4 - 2*Q4)*Lu)*polylog(2,-1 + (Q2*(-1 + v))/(2.*m2)) - 
            6*(16*m4 - Q4)*(2*polylog(3,u) + 4*polylog(3,-1 + (Q2*(-1 + v))/(2.*m2)) + Zeta3)))/(Q4*t) + 
       (2*(-4*Q2*(-8*m4 + 2*m2*Q2 + Q4)*(-1 + 2*v*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*mp.log((Q2*(-1 + v))/m2) - 
            4*Q2*(-2*m2 + Q2)*t*mp.log(4/(1 + v)) + mp.log(1 - (Q2*(-1 + v))/(2.*m2))*
             (mp.log(1 - (Q2*(-1 + v))/(2.*m2))*(3*Q6*(-1 + v) - 32*m**6*(-3 +mp.log(16)) + m2*Q4*(-8 + 6*v + mp.log(16)) - 
                  4*m4*Q2*(-10 + 15*v + mp.log(16)) + 8*m2*(-32*m4 - 4*m2*Q2 + Q4)*mp.log(2 - (Q2*(-1 + v))/(2.*m2))) + 
               4*(Q2*(4*m4 + 2*m2*Q2 + Q4)*v + m2*(-32*m4 - 4*m2*Q2 + Q4)*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*
                mp.log(1/(1 + v)) + 4*Q2*v*((-52*m4 + 10*m2*Q2 + 5*Q4)*mp.log(2) + 
                  (40*m4 - 4*m2*Q2 - 2*Q4)*mp.log(4 + (Q2 - Q2*v)/m2))) + 
            8*(Q2*(-2*m4 + 2*m2*Q2 + Q4)*v + 2*m2*(-32*m4 - 4*m2*Q2 + Q4)*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*
             polylog(2,1 - (Q2*(-1 + v))/(2.*m2)) - 
            8*(Q2*(-20*m4 + 2*m2*Q2 + Q4)*v + 4*m2*(8*m2 - Q2)*t*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*
             polylog(2,-1 + (Q2*(-1 + v))/(2.*m2)) - 
            12*t*(Q2*(-2*m2 + Q2)*v*polylog(2,u) - 
               m2*(8*m2 - Q2)*(2*polylog(3,1 - (Q2*(-1 + v))/(2.*m2)) + 4*polylog(3,-1 + (Q2*(-1 + v))/(2.*m2)) + Zeta3))))
         /(Q4*t)
			)

def adler_hq_full_one_loop_OS(Q,m):

	"""
		Description
		-----------
		Full contribution of to the Adler function at order $\alpha^{1}_s$ in the ON-shell scheme. 
		
		Parameters
		----------
		Q : float or mp complex number.
			The scale at which the  Adler function wants to be computed. 
		m : float
			Pole mass.
		Returns
		----------
		If complex number was used as input, returns a complex number. If positive real, returns a real number. 
		IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges and by $\hat{\\alpha}_s/pi$.     
	"""
	m2=m**2;
	m4=m2**2;
	Q2=Q**2;
	Q4=Q2**2;
	Q6=Q2**3;
	u=(2*m**2 + Q2 - mp.sqrt(1 + (4*m**2)/Q2)*Q2)/(2.*m**2);
	Lu=mp.log(u)
	v=mp.sqrt(1 + (4*m**2)/Q2)
	t=4*m**2 + Q2
	return ((Q2*(-44*m2 + 3*Q2) - (12*m2*(9*m2 + Q2)*Lu)/mp.sqrt(1 + (4*m2)/Q2))/Q4 - 
       (4*m2*Lu*(m2 + 4*Q2 + (m2 + 2*Q2)*v*Lu))/(mp.sqrt(1 + (4*m2)/Q2)*Q4) + 
       (4*m2*(Lu*(4*Q2*(-2*m2 + Q2)*v*mp.log(2/(1 + v)) + 8*Q2*(-2*m2 + Q2)*v*mp.log((t - Q2*v)/(2.*m2)) + 
               Lu*(-((2*m2 - Q2)*(4*m2 - 3*Q2*(-1 + v))) + 
                  2*(16*m4 - Q4)*(mp.log(1/(2 + 2*v)) + 2*mp.log(4 + (Q2 - Q2*v)/m2)))) + 
            4*(Q2*(-2*m2 + Q2)*v + (32*m4 - 2*Q4)*Lu)*polylog(2,u) + 
            8*(Q2*(-2*m2 + Q2)*v + (32*m4 - 2*Q4)*Lu)*polylog(2,-1 + (Q2*(-1 + v))/(2.*m2)) - 
            6*(16*m4 - Q4)*(2*polylog(3,u) + 4*polylog(3,-1 + (Q2*(-1 + v))/(2.*m2)) + Zeta3)))/(Q4*t) + 
       (2*(-4*Q2*(-8*m4 + 2*m2*Q2 + Q4)*(-1 + 2*v*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*mp.log((Q2*(-1 + v))/m2) - 
            4*Q2*(-2*m2 + Q2)*t*mp.log(4/(1 + v)) + mp.log(1 - (Q2*(-1 + v))/(2.*m2))*
             (mp.log(1 - (Q2*(-1 + v))/(2.*m2))*(3*Q2**3*(-1 + v) - 32*m**6*(-3 + mp.log(16)) + m2*Q4*(-8 + 6*v + mp.log(16)) - 
                  4*m4*Q2*(-10 + 15*v + mp.log(16)) + 8*m2*(-32*m4 - 4*m2*Q2 + Q4)*mp.log(2 - (Q2*(-1 + v))/(2.*m2))) + 
               4*(Q2*(4*m4 + 2*m2*Q2 + Q4)*v + m2*(-32*m4 - 4*m2*Q2 + Q4)*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*
               mp.log(1/(1 + v)) + 4*Q2*v*((-52*m4 + 10*m2*Q2 + 5*Q4)*mp.log(2) + 
                  (40*m4 - 4*m2*Q2 - 2*Q4)*mp.log(4 + (Q2 - Q2*v)/m2))) + 
            8*(Q2*(-2*m4 + 2*m2*Q2 + Q4)*v + 2*m2*(-32*m4 - 4*m2*Q2 + Q4)*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*
             polylog(2,1 - (Q2*(-1 + v))/(2.*m2)) - 
            8*(Q2*(-20*m4 + 2*m2*Q2 + Q4)*v + 4*m2*(8*m2 - Q2)*t*mp.log(1 - (Q2*(-1 + v))/(2.*m2)))*
             polylog(2,-1 + (Q2*(-1 + v))/(2.*m2)) - 
            12*t*(Q2*(-2*m2 + Q2)*v*polylog(2,u) - 
               m2*(8*m2 - Q2)*(2*polylog(3,1 - (Q2*(-1 + v))/(2.*m2)) + 4*polylog(3,-1 + (Q2*(-1 + v))/(2.*m2)) + Zeta3))))
         /(Q4*t))



#Adler function in the high energy expansion, outer heavy quark, inner massless quarks. MS scheme. 
def adler_he_o_heavy_i_massless_Q_supressed_MS(m,Q,mu,asmu,nq,k,nloops=5):
    """
        Description
        -----------
        
        Massive contributions to the high energy expansion of the connected contribution to the Adler function in the MSbar scheme. 
        In this expresssion the external quark is massive while the inner quarks are consider to be massless. 
        This is obtained from the expansion given in https://arxiv.org/abs/1110.5581. Please note 
        that the URL given in such paper changed. Now it is: https://www.ttp.kit.edu/Progdata/ttp11/ttp11-25/. 
        At order asmu**2 30 terms in the expansion are included. At order asmu**3 only the first term in the expansion. Such term is taken from 
        https://arxiv.org/pdf/2302.01359.pdf  eq.(3.9) specifically from appendix A.17.
        
        
        Parameters
        ----------
        
        m: MSbar mass of the external quark at the renormalization scale mu. 
        
        Q : float or mp complex number.
            The scale at which the  Adler function wants to be computed. 
        
        mu : float
            Renormalization scale. 
        
        asmu : float
            Strong coupling constant at scale mu. 
        
        nq: number of internal quarks INCLUDING the heavy quark i.e nq=nl+1.
        
        k: number of terms in the m^2/s expansion that are to be included.
        
        nloops : int, optional
            The number of loops at which the Adler function is to be evaluated. nloops=5 is the default value which includes 
            the terms up to order asmu**3; To include only terms up to  order asmu**2 use nloops=2.
        
        Returns
        ----------
        
        If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges.   
        
        IMPORTANT: Only the s supressed terms are included here. The masseless contribution needs to be included through the functions 
        adler_massless_connected and adler_massless_disconnected
        
    """
    npower=k;
    d=0;
    x=(m**2)/(Q**2)
    Lz=mp.log(Q**2/m**2);
    Lz2=Lz**2;
    Lz3=Lz**3;
    Lq=mp.log(Q**2/mu**2);
    a=asmu/np.pi;
    d0=[-6.,12.*Lz,24. - 24.*Lz,-84. + 72.*Lz,296. - 240.*Lz,-1066. + 840.*Lz,
        3904.8 - 3024.*Lz,-14485.6 + 11088.*Lz,54256.2285714285714285714285714 - 41184.*Lz,
        -204747.857142857142857142857143 + 154440.*Lz,777305.238095238095238095238095 - 583440.*Lz,
        -2.96542870476190476190476190476e6 + 2.217072e6*Lz,1.13591917818181818181818181818e7 - 8.465184e6*Lz,
        -4.3661140496969696969696969697e7 + 3.2449872e7*Lz,1.68311485603729603729603729604e8 - 1.248072e8*Lz,
        -6.50474987328671328671328671329e8 + 4.813992e8*Lz,2.5194490550041958041958041958e9 - 1.86141024e9*Lz,
        -9.77740735564125874125874125874e9 + 7.21296468e9*Lz,3.80092629148425339366515837104e10 - 2.800327464e10*Lz,
        -1.47986659944387631975867269985e11 + 1.089016236e11*Lz,5.76972429720246566642851472573e11 - 4.241431656e11*Lz,
        -2.25231319173696160990712074303e12 + 1.65415834584e12*Lz,8.80224860059575485773256671089e12 - 6.45909449328e12*Lz,
        -3.44354804572597689893182153244e13 + 2.524918756464e13*Lz,1.34842992290466922132114755617e14 - 9.88011687312e13*Lz,
        -5.28478112751312111684116126168e14 + 3.869712441972e14*Lz,2.07287250996657451780173521458e15 - 1.516927277253024e15*Lz,
        -8.13652625885482495445296122642e15 + 5.951022395377248e15*Lz,3.19597259226793738211856996296e16 - 2.3363273107777344e16*Lz,
        -1.25615666311311257726086677116e17 + 9.178428720912528e16*Lz]
    powers = np.arange(1,len(d0[0:npower])+1)
    terms = [d0[i-1] * (x**i) for i in powers]
    d+=sum(terms)
    if(nloops>0):
        d1=[-28. + 12.*Lq,
            17.7991542344404 + 24.*Lq + 44.*Lz - 48.*Lq*Lz + 24.*Lz2,
            173.62962962963 - 192.*Lq - 135.111111111111*Lz + 144.*Lq*Lz - 66.666666666667*Lz2,
            -1047.75925925926 + 816.*Lq + 524.22222222222*Lz - 576.*Lq*Lz + 305.333333333333*Lz2,
            4919.10666666667 - 3440.*Lq - 2003.76296296296*Lz + 2400.*Lq*Lz - 1360.88888888889*Lz2,
            -21620.6725925926 + 14472.*Lq + 7862.4888888889*Lz - 10080.*Lq*Lz + 5994.6666666667*Lz2,
            92683.972051398 - 60715.2*Lq - 31256.4368253968*Lz + 42336.*Lq*Lz - 26130.1333333333*Lz2,
            -392223.712432603 + 253945.6*Lq + 125028.845502646*Lz - 177408.*Lq*Lz + 112861.777777778*Lz2,
            1.6465138473533e6 - 1.05898011428571e6*Lq - 501603.62842026*Lz + 741312.*Lq*Lz - 483705.523809524*Lz2,
            -6.87300193735156e6 + 4.40383714285714e6*Lq + 2.01511081058201e6*Lz - 3.0888e6*Lq*Lz + 2.05953733333333e6*Lz2,
            2.85679838690199e7 - 1.82675952380952e7*Lq - 8.09978723458928e6*Lz + 1.283568e7*Lq*Lz - 8.72065362962963e6*Lz2,
            -1.18344913405404e8 + 7.56044329142857e7*Lq + 3.25613296764214e7*Lz - 5.3209728e7*Lq*Lz + 3.67515034666667e7*Lz2,
            4.88901597163656e8 - 3.12269354327273e8*Lq - 1.30884815803477e8*Lz + 2.20094784e8*Lq*Lz - 1.54254416969697e8*Lz2,
            -2.01505969658731e9 + 1.28741167791515e9*Lq + 5.2600092885035e8*Lz - 9.08596416e8*Lq*Lz + 6.45168707555556e8*Lz2,
            8.28886446074828e9 - 5.29895896811189e9*Lq - 2.11334768772405e9*Lz + 3.744216e9*Lq*Lz - 2.69015296082051e9*Lz2,
            -3.40374496560158e10 + 2.17779979945175e10*Lq + 8.48855713739794e9*Lz - 1.54047744e10*Lq*Lz + 1.11869113933333e10*Lz2,
            1.39561400689514e11 - 8.93840883501427e10*Lq - 3.40858746621104e10*Lz + 6.328794816e10*Lq*Lz - 4.64096218295111e10*Lz2,
            -5.71471651406334e11 + 3.66412594163085e11*Lq + 1.36834657253553e11*Lz - 2.5966672848e11*Lq*Lz + 1.92125181004667e11*Lz2,
            2.33726069652895e12 - 1.50035854004402e12*Lq - 5.49167165806613e11*Lz + 1.06412443632e12*Lq*Lz - 7.93844848432627e11*Lz2,
            -9.54893386823999e12 + 6.13726964497551e12*Lq + 2.20346690662141e12*Lz - 4.356064944e12*Lq*Lz + 3.27449791021126e12*Lz2,
            3.89746532298323e13 - 2.50811283794504e13*Lq - 8.83912113847235e12*Lz + 1.78140129552e13*Lq*Lz - 1.34859867401446e13*Lz2,
            -1.58937872769762e14 + 1.02410097128106e14*Lq + 3.54502450901101e13*Lz - 7.278296721696e13*Lq*Lz + 5.54640191561685e13*Lz2,
            6.47624560659847e14 - 4.17821624613965e14*Lq - 1.42148980112149e14*Lz + 2.9711834669088e14*Lq*Lz - 2.2781603913526e14*Lz2,
            -2.63693129418992e15 + 1.70340143707775e15*Lq + 5.69887283745935e14*Lz - 1.21196100310272e15*Lq*Lz + 9.34649357876235e14*Lz2,
            1.07294933428217e16 - 6.93975195198575e15*Lq - 2.28434042318021e15*Lz + 4.94005843656e15*Lq*Lz - 3.83041713523374e15*Lz2,
            -4.36301668918596e16 + 2.82548043514626e16*Lq + 9.15513609351449e15*Lz - 2.01225046982544e16*Lq*Lz + 1.56824204061147e16*Lz2,
            1.77313441556253e17 - 1.14968970092701e17*Lq - 3.66864718568653e16*Lz + 8.19140729716633e16*Lq*Lz - 6.41478950796022e16*Lz2,
            -7.20213577574753e17 + 4.67547515286625e17*Lq + 1.46990368740227e17*Lz - 3.33257254141126e17*Lq*Lz + 2.62170098231076e17*Lz2,
            2.92389459293195e18 - 1.90039064973096e18*Lq - 5.88867837946236e17*Lz + 1.35506984025109e18*Lq*Lz - 1.070634993007e18*Lz2,
            -1.18647119790017e19 + 7.72050855309693e18*Lq + 2.3588302576379e18*Lz - 5.50705723254752e18*Lq*Lz + 4.36898662351722e18*Lz2]
        powers = np.arange(1,len(d1[0:npower])+1)
        terms = [d1[i-1] * (x**i) for i in powers]
        d+=a*sum(terms)
    
    if(nloops>1):
        
        d2=[-295.098738766051 + 183.5*Lq - 28.5*Lq**2 + 12.25*nq - 6.33333333333333*Lq*nq + Lq**2*nq,
            473.0850292825 + 68.85570891753*Lq - 129.*Lq**2 + 423.6666666667*Lz - 403.*Lq*Lz + 
            162.*Lq**2*Lz + 195.*Lz2 - 162.*Lq*Lz2 + 54.*Lz3 - 26.71593836855*nq - 0.3668076275933*Lq*nq + 
            2.*Lq**2*nq - 16.44444444444*Lz*nq + 14.*Lq*Lz*nq - 4.*Lq**2*Lz*nq - 6.666666666667*Lz2*nq + 
            4.*Lq*Lz2*nq - 1.333333333333*Lz3*nq,
            
            1010.8469390353 - 2597.481481481481481481481*Lq + 984.*Lq**2 - 1453.027708078*Lz + 
            1521.555555555555555555556*Lq*Lz - 630.*Lq**2*Lz - 714.2283950617*Lz2 + 
            583.333333333333333333333*Lq*Lz2 - 182.4197530864197530864198*Lz3 - 11.232662609139*nq + 
            55.6049382716049382716049*Lq*nq - 16.*Lq**2*nq + 70.2592592592592592592593*Lz*nq - 42.5185185185185185185185*Lq*Lz*nq + 
            12.*Lq**2*Lz*nq + 20.44444444444*Lz2*nq - 11.11111111111111111111111*Lq*Lz2*nq + 2.37037037037*Lz3*nq,
            
            -11058.925448125 + 15745.85648148*Lq - 4962.*Lq**2 + 5531.186408289*Lz - 6838.055555556*Lq*Lz + 
            3096.*Lq**2*Lz + 3851.031893004*Lz2 - 3282.333333333*Lq*Lz2 + 1010.115226337448559670782*Lz3 + 
            266.8573673272*nq - 287.9598765432098765432099*Lq*nq + 68.*Lq**2*nq - 260.2067901235*Lz*nq + 
            167.3703703703703703703704*Lq*Lz*nq - 48.*Lq**2*Lz*nq - 96.09259259259*Lz2*nq + 50.8888888888888888888889*Lq*Lz2*nq - 
            9.40740740740740740740741*Lz3*nq,
            
            65764.47253758 - 81202.80259259*Lq + 24330.*Lq**2 - 20588.7855749*Lz + 30204.42222222*Lq*Lz - 15300.*Lq**2*Lz - 
            20073.92393519*Lz2 + 17351.33333333*Lq*Lz2 - 5282.384979424*Lz3 - 1518.127438204*nq + 
            1297.628888888888888888889*Lq*nq - 286.6666666666666666666667*Lq**2*nq + 
            980.2213168724*Lz*nq - 667.293827160493827160494*Lq*Lz*nq + 200.*Lq**2*Lz*nq + 442.251851851851851851852*Lz2*nq - 
            226.8148148148148148148148*Lq*Lz2*nq + 40.04938271605*Lz3*nq,
            
            -341370.4930618 + 395532.8985185*Lq - 116811.*Lq**2 + 76521.94291392*Lz - 134413.0444444*Lq*Lz + 
            74340.*Lq**2*Lz + 103257.95324074*Lz2 - 88421.33333333*Lq*Lz2 + 26625.1237037*Lz3 + 7229.871022589*nq -
            5613.445432099*Lq*nq + 1206.*Lq**2*nq - 3743.202222222*Lz*nq + 2710.414814815*Lq*Lz*nq - 840.*Lq**2*Lz*nq - 
            1985.740740741*Lz2*nq + 999.1111111111*Lq*Lz2*nq - 172.74074074074074074074*Lz3*nq,
            
            1.690769534229e6 - 1.870479205512e6*Lq + 550825.8*Lq**2 - 279082.5117998*Lz + 597188.7834921*Lq*Lz - 
            354564.*Lq**2*Lz - 528829.3483542*Lz2 + 437679.7333333*Lq*Lz2 - 128943.2785655*Lz3 - 32317.8529613*nq + 
            23879.9953419*Lq*nq - 5059.6*Lq**2*nq + 14460.79184681*Lz*nq - 11089.406137566*Lq*Lz*nq + 3528.*Lq**2*Lz*nq +
            8769.772698413*Lz2*nq - 4355.022222222*Lq*Lz2*nq + 744.4148148148*Lz3*nq,
           
            -8.281983329928e6 + 8.67294003245e6*Lq - 2.558148e6*Lq**2 + 940862.4959971*Lz - 2.6394357420635e6*Lq*Lz +
            1.6632e6*Lq**2*Lz + 2.742560677023e6*Lz2 - 2.1161583333333e6*Lq*Lz2 + 595372.1049064*Lz3 + 140164.5121051*nq - 
            100640.84096099*Lq*nq + 21162.13333333*Lq**2*nq - 56296.06346246*Lz*nq + 45478.14091711*Lq*Lz*nq - 14784.*Lq**2*Lz*nq -
            38261.76358025*Lz2*nq + 18810.2962963*Lq*Lz2*nq - 3193.30864198*Lz3*nq,
            
            4.1211073718618e7 - 3.9624910903707e7*Lq + 1.17282306857143e7*Lq**2 - 2.26466798406194e6*Lz +
            1.15931411944822e7*Lq*Lz - 7.691112e6*Lq**2*Lz - 1.478628519523e7*Lz2 + 1.00368896190476e7*Lq*Lz2 - 
            2.5576023544094e6*Lz3 - 597590.2059718*nq + 421499.546*Lq*nq - 88248.343*Lq**2*nq + 220239.26*Lz*nq - 
            186560.605*Lq*Lz*nq + 61776.*Lq**2*Lz*nq + 165355.51*Lz2*nq - 80617.587*Lq*Lz2*nq + 13625.418*Lz3*nq,
           
            -2.15098130348823e8 + 1.78923830338769e8*Lq - 5.31824475e7*Lq**2 - 5.7157938598038e6*Lz -
            5.0604321607407e7*Lq*Lz + 3.51351e7*Lq**2*Lz + 8.6052504606699e7*Lz2 - 4.6854474333333e7*Lq*Lz2 +
            9.4155439436636e6*Lz3 + 2.520268207708e6*nq - 1.757144370511e6*Lq*nq + 366986.4285714*Lq**2*nq - 
            864309.2344*Lz*nq + 764851.8017637*Lq*Lz*nq - 257400.*Lq**2*Lz*nq - 709162.0066138*Lz2*nq + 
            343256.2222222*Lq*Lz2*nq - 57839.62962963*Lz3*nq,
            
            1.22858211669373e9 - 8.00133305e8*Lq + 2.38897171e8*Lq**2 + 1.78620163531612e8*Lz + 2.1960394e8*Lq*Lz - 
            1.5884154e8*Lq**2*Lz - 5.64223736606758e8*Lz2 + 2.15836177e8*Lq*Lz2 - 1.88576165204713e7*Lz3 - 1.0549566519362e7*nq + 
            7.29849665e6*Lq*nq - 1.5222996e6*Lq**2*nq + 3.398681984103e6*Lz*nq - 3.13269787e6*Lq*Lz*nq + 1.06964e6*Lq**2*Lz*nq + 
            3.022207976819e6*Lz2*nq - 1.45344227e6*Lq*Lz2*nq + 244383.0781893*Lz3*nq,
            
            -8.02975066361053e9 + 3.5490177481284e9*Lq - 1.06441901822857e9*Lq**2 - 2.41901447423585e9*Lz - 9.479338269776e8*Lq*Lz + 
            7.11680112e8*Lq**2*Lz + 4.28699799568297e9*Lz2 - 9.8310271773333e8*Lq*Lz2 - 1.60791024973464e8*Lz3 + 4.3917752131e7*nq -
            3.0224767916774e7*Lq*nq + 6.3003694095238e6*Lq**2*nq - 1.33814524923e7*Lz*nq + 1.28171282794036e7*Lq*Lz*nq - 4.434144e6*Lq**2*Lz*nq - 
            1.28113178962e7*Lz2*nq + 6.1252505777778e6*Lq*Lz2*nq - 1.02827777778e6*Lz3*nq,
            
            6.14850432222697e10 - 1.563182408e10*Lq + 4.708966752e9*Lq**2 + 2.88371926065033e10*Lz + 4.072153002e9*Lq*Lz - 
            3.16386252e9*Lq**2*Lz - 3.7570200844283e10*Lz2 + 4.434814488e9*Lq*Lz2 + 3.30256683758396e9*Lz3 - 1.82063088524601e8*nq +
            1.248543432e8*Lq*nq - 2.602244619e7*Lq**2*nq + 5.27279111050459e7*Lz*nq - 5.238285597e7*Lq*Lz*nq + 1.8341232e7*Lq**2*Lz*nq +
            5.40624060715762e7*Lz2*nq - 2.570906949e7*Lq*Lz2*nq + 4.31075886868687e6*Lz3*nq,
            
            -5.44253868222931e11 + 6.84329450056533e10*Lq - 2.07025509639455e10*Lq**2 - 3.35678467695154e11*Lz - 1.7417530315926e10*Lq*Lz +
            1.3969669896e10*Lq**2*Lz + 3.68263681229362e11*Lz2 - 1.98389377573333e10*Lq*Lz2 - 4.26664167442569e10*Lz3 + 7.522434666e8*nq - 
            5.14650460252767e8*Lq*nq + 1.07284306492929e8*Lq**2*nq - 2.078664543e8*Lz*nq + 2.13860768141725e8*Lq*Lz*nq - 7.5716368e7*Lq**2*Lz*nq -
            2.272483557e8*Lz2*nq + 1.07528117925926e8*Lq*Lz2*nq - 1.801306904e7*Lz3*nq,
            
            5.369082476e12 - 2.979867921e11*Lq + 9.05146691e10*Lq**2 + 3.928147473e12*Lz + 7.420843393e10*Lq*Lz - 6.1311537e10*Lq**2*Lz - 
            3.899252221e12*Lz2 + 8.810250947e10*Lq*Lz2 + 5.009626919e11*Lz3 - 3.099687388e9*nq + 2.117443933e9*Lq*nq - 4.41579914e8*Lq**2*nq +
            8.196735972e8*Lz*nq - 8.722546146e8*Lq*Lz*nq + 3.12018e8*Lq**2*Lz*nq + 9.519843421e8*Lz2*nq - 4.483588268e8*Lq*Lz2*nq + 7.505410908e7*Lz3*nq,
            
            -5.69539953002303e13 + 1.29142756471494e12*Lq - 3.93797489554741e11*Lq**2 - 4.66148580988934e13*Lz - 3.15058140551245e11*Lq*Lz +
            2.676579552e11*Lq**2*Lz + 4.34633923384314e13*Lz2 - 3.88745170918333e11*Lq*Lz2 - 5.78496350964322e12*Lz3 + 1.27437617212369e10*nq - 
            8.69763021968562e9*Lq*nq + 1.81483316620979e9*Lq**2*nq - 3.2325506143443e9*Lz*nq + 3.55431152289966e9*Lq*Lz*nq - 1.2837312e9*Lq**2*Lz*nq - 
            3.97615182662063e9*Lz2*nq + 1.86448523222222e9*Lq*Lz2*nq - 3.11927334656085e8*Lz3*nq,
            
            6.339232142e14 - 5.573211263e12*Lq + 1.705720572e12*Lq**2 + 5.620440482e14*Lz + 1.333354188e12*Lq*Lz - 1.162916047e12*Lq**2*Lz - 
            5.020274196e14*Lz2 + 1.705553602e12*Lq*Lz2 + 6.737726432e13*Lz3 - 5.22934528e10*nq + 3.567469016e10*Lq*nq - 7.448674029e9*Lq**2*nq + 
            1.274829373e10*Lz*nq - 1.447097191e10*Lq*Lz*nq + 5.27399568e9*Lq**2*Lz*nq + 1.656342181e10*Lz2*nq - 7.734936972e9*Lq*Lz2*nq + 
            1.293434003e9*Lz3*nq,
            
            -7.29767790761266e15 + 2.39601821402722e13*Lq - 7.35891074e12*Lq**2 - 6.88270956673149e15*Lz - 5.62660639357653e12*Lq*Lz + 
            5.031042864e12*Lq**2*Lz + 5.95421714740471e15*Lz2 - 7.44485076393083e12*Lq*Lz2 - 7.97699832810278e14*Lz3 + 2.14231510966688e11*nq - 
            1.46135913312595e11*Lq*nq + 3.053438285e10*Lq**2*nq - 5.0272295669531e10*Lz*nq + 5.88705996089256e10*Lq*Lz*nq - 2.163889404e10*Lq**2*Lz*nq - 
            6.88361995897502e10*Lz2*nq + 3.20208635007778e10*Lq*Lz2*nq - 5.35241597485185e9*Lz3*nq,
            
            8.61796579795226e16 - 1.02655716571187e14*Lq + 3.163392969e13*Lq**2 + 8.5509211305671e16*Lz +
            2.3681372949069e13*Lq*Lz - 2.168153539e13*Lq**2*Lz - 7.21202054226327e16*Lz2 + 3.23491775736e13*Lq*Lz2 +
            9.61352988102838e15*Lz3 - 8.76391750458445e11*nq + 5.97926579983161e11*Lq*nq - 1.250298783e11*Lq**2*nq + 
            1.98222010768319e11*Lz*nq - 2.39322921567769e11*Lq*Lz*nq + 8.867703636e10*Lq**2*Lz*nq + 2.85476245943615e11*Lz2*nq - 
            1.32307474738771e11*Lq*Lz2*nq + 2.210847918522e10*Lz3*nq,
            
            -1.03888441990239e18 + 4.38451533103108e14*Lq - 1.35540203605351e14*Lq**2 - 1.07643659814011e18*Lz - 9.94319919232202e13*Lq*Lz + 
            9.3110888178e13*Lq**2*Lz + 8.89023011053347e17*Lz2 - 1.399847857e14*Lq*Lz2 - 1.17829901525852e17*Lz3 + 3.58069238824e12*nq -
            2.44388753984e12*Lq*nq + 5.11439137081292e11*Lq**2*nq - 7.8145567547e11*Lz*nq + 9.72253504437e11*Lq*Lz*nq - 3.63005412e11*Lq**2*Lz*nq - 
            1.18168126907e12*Lz2*nq + 5.45749651702e11*Lq*Lz2*nq - 9.11691832364e10*Lz3*nq,
            
            1.2743322123e19 - 1.86734372290879e15*Lq + 5.790042604e14*Lq**2 + 1.37140695336e19*Lz + 4.16574028506e14*Lq*Lz - 
            3.985885399e14*Lq**2*Lz - 1.11258991048e19*Lz2 + 6.03497906621469e14*Lq*Lz2 + 1.46651720493e18*Lz3 - 1.46133952972e13*nq +
            9.97926559100682e12*Lq*nq - 2.090094032e12*Lq**2*nq + 3.08016018354e12*Lz*nq - 3.94735532241206e12*Lq*Lz*nq + 1.48450108e12*Lq**2*Lz*nq + 
            4.88299564896e12*Lz2*nq - 2.24766445669076e12*Lq*Lz2*nq + 3.75391271721e11*Lz3*nq,
            
            -1.586930266e20 + 7.93222186758e15*Lq - 2.46661898759e15*Lq**2 - 1.766343456e20*Lz - 
            1.74173786838e15*Lq*Lz + 1.7013018587e15*Lq**2*Lz + 1.410994755e20*Lz2 - 2.59294289555e15*Lq*Lz2 -
            1.850500149e19*Lz3 + 5.95802004839843e13*nq - 4.07132700628e13*Lq*nq + 8.53417476068e12*Lq**2*nq - 
            1.2138051277518e13*Lz*nq + 1.60171196285e13*Lq*Lz*nq - 6.06524726808e12*Lq**2*Lz*nq - 2.01463235845994e13*Lz2*nq +
            9.24400319269e12*Lq*Lz2*nq - 1.54356690450335e12*Lz3*nq,
            
            2.00276334000567e21 - 3.36143279626423e16*Lq + 1.04815204466563e16*Lq**2 + 
            2.29771303400066e21*Lz + 7.26887166625037e15*Lq*Lz - 7.2422597005902e15*Lq**2*Lz -
            1.8107105318402e21*Lz2 + 1.11060319078439e16*Lq*Lz2 + 2.36395002771099e20*Lz3 - 
            2.426960859e14*nq + 1.65968207973025e14*Lq*nq - 3.48184687178304e13*Lq**2*nq + 4.782155956e13*Lz*nq - 
            6.49579337257582e13*Lq*Lz*nq + 2.475986222424e13*Lq**2*Lz*nq + 8.30018801e13*Lz2*nq - 3.79693398558767e13*Lq*Lz2*nq + 6.339033418e12*Lz3*nq,
            
            -2.557892899e22 + 1.421325188e17*Lq - 4.443577247e16*Lq**2 - 3.016185583e22*Lz - 3.028351811e16*Lq*Lz + 
            3.075351045e16*Lq**2*Lz + 2.348459802e22*Lz2 - 4.743345491e16*Lq*Lz2 - 3.053470094e21*Lz3 + 9.878032199e14*nq - 
            6.76072082e14*Lq*nq + 1.419501198e14*Lq**2*nq - 1.883612266e14*Lz*nq + 2.633091311e14*Lq*Lz*nq - 1.009967503e14*Lq**2*Lz*nq -
            3.415187857e14*Lz2*nq + 1.55774893e14*Lq*Lz2*nq - 2.600291006e13*Lz3*nq,
            
            3.30220278109216e23 - 5.99754244144813e17*Lq + 1.87976016170184e17*Lq**2 + 3.99241022953593e23*Lz +
            1.25966701369011e17*Lq*Lz - 1.3029404126427e17*Lq**2*Lz - 3.07529869950084e23*Lz2 + 2.020545039e17*Lq*Lz2 + 
            3.98373642845763e22*Lz3 - 4.017507122e15*nq + 2.75210332824609e15*Lq*nq - 5.78312662665479e14*Lq**2*nq +
            7.417324033e14*Lz*nq - 1.06684263116337e15*Lq*Lz*nq + 4.1167153638e14*Lq**2*Lz*nq + 1.403529493e15*Lz2*nq - 
            6.38402855872291e14*Lq*Lz2*nq + 1.065521072e14*Lz3*nq,
            
            -4.30485995625445e24 + 2.52596754449541e18*Lq - 7.93597773819544e17*Lq**2 - 5.32522549550146e24*Lz - 
            5.2319622676728e17*Lq*Lz + 5.50853566114714e17*Lq**2*Lz + 4.06242105653323e24*Lz2 - 8.58612517234779e17*Lq*Lz2 -
            5.2448071081623e23*Lz3 + 1.63285982082769e16*nq - 1.11959728641242e16*Lq*nq + 2.35456702928855e15*Lq**2*nq - 2.92002549652948e15*Lz*nq + 
            4.32064833478775e15*Lq*Lz*nq - 1.6768753915212e15*Lq**2*Lz*nq - 5.76168184352245e15*Lz2*nq + 2.61373673435245e15*Lq*Lz2*nq - 
            4.36193017340393e14*Lz3*nq,
            
            5.66205715106741e25 - 1.06197385e19*Lq + 3.34415859935206e18*Lq**2 + 7.15336000262419e25*Lz + 
            2.170087421e18*Lq*Lz - 2.32431182057095e18*Lq**2*Lz - 5.40941583917152e25*Lz2 + 3.640393046e18*Lq*Lz2 +
            6.96249660042766e24*Lz3 - 6.632407011e16*nq + 4.552015277e16*Lq*nq - 9.58074750772509e15*Lq**2*nq + 1.149227059e16*Lz*nq - 
            1.749136656e16*Lq*Lz*nq + 6.82617274763861e15*Lq**2*Lz*nq + 2.36283734e16*Lz2*nq - 1.069131585e16*Lq*Lz2*nq + 
            1.784035635e15*Lz3*nq,
            
            -7.50800377433457e26 + 4.457412421e19*Lq - 1.406746552e19*Lq**2 - 
            9.67214937108341e26*Lz - 8.989461382e18*Lq*Lz + 9.78943184e18*Lq**2*Lz + 
            7.25603813140066e26*Lz2 - 1.540249327e19*Lq*Lz2 - 9.31314463669751e25*Lz3 + 2.692430739e17*nq - 
            1.849727512e17*Lq*nq + 3.896229294e16*Lq**2*nq - 4.521695422e16*Lz*nq + 7.078412453e16*Lq*Lz*nq - 
            2.777143785e16*Lq**2*Lz*nq - 9.680714121e16*Lz2*nq + 4.369501637e16*Lq*Lz2*nq - 7.290624881e15*Lz3*nq,
            
            1.00305599676134e28 - 1.86801809514126e20*Lq + 5.90794358258289e19*Lq**2 +
            1.3157477e28*Lz + 3.71937667609291e19*Lq*Lz - 4.11602463976267e19*Lq**2*Lz - 
            9.79902664478136e27*Lz2 + 6.50410758251755e19*Lq*Lz2 + 1.25446951414394e27*Lz3 - 
            1.09241499418518e18*nq + 7.51258911284624e17*Lq*nq - 1.5836588747758e17*Lq**2*nq +
            1.77856459838958e17*Lz*nq - 2.86348784137023e17*Lq*Lz*nq + 1.1292248668759e17*Lq**2*Lz*nq + 
            3.96276991434881e17*Lz2*nq - 1.78439165501167e17*Lq*Lz2*nq + 2.97706134215235e16*Lz3*nq,
            
            -1.34935267816219e29 + 7.81718810691913e20*Lq - 2.47738013085964e20*Lq**2 - 1.80001397192663e29*Lz -
            1.53716184693014e20*Lq*Lz + 1.72783920671178e20*Lq**2*Lz + 1.33161869772018e29*Lz2 - 2.74153910625705e20*Lq*Lz2 - 
            1.70068541541477e28*Lz3 + 4.43013614676611e18*nq - 3.04974485109707e18*Lq*nq + 6.43375712758077e17*Lq**2*nq - 
            6.99370852037635e17*Lz*nq + 1.15800743634903e18*Lq*Lz*nq - 4.58921436045626e17*Lq**2*Lz*nq - 1.62081781252082e18*Lz2*nq + 
            7.28164437252869e17*Lq*Lz2*nq - 1.21477402657311e17*Lz3*nq]    
        
        powers = np.arange(1,len(d2[0:npower])+1)
        terms = [d2[i-1] * (x**i) for i in powers]
        d+=a*a*sum(terms)
    if(nloops>2):
        # WARNING!!! Care is needed with this terms, please only use it for tails. As one can see from the previous orders the 
        # terms  in the expansion m^n/Q^n have a strong oscilations which cancell each other. 
        #To convince yourself run the following:
        #print(d2[0])
        #print(d2[1])
        #print(d2[2])
        #print(d2[3])
        # I took this terms from https://arxiv.org/pdf/2302.01359.pdf  eq.(3.9) specifically A.17
        d3=[-3829.2034126333792 + 2861.594707412049*Lq - 776.875*Lq**2 + 71.25*Lq**3 + 365.8721486473844*nq - 247.5951486202796*Lq*nq + 
            60.75*Lq**2*nq - 5.666666666666667*Lq**3*nq - 5.236773962019004*nq**2 + 3.759259259259259*Lq*nq**2 - 
            1.0555555555555556*Lq**2*nq**2 + 0.1111111111111111*Lq**3*nq**2]
        
        powers = np.arange(1,len(d3[0:npower])+1)
        terms = [d3[i-1] * (x**i) for i in powers]
        d+=a*a*a*sum(terms)
    return 3*d;


def adler_he_o_heavy_i_massless_Q_supressed_OS(m,Q,mu,asmu,nq,k,nloops=5):
	"""
        Description
        -----------
        
        Massive contributions to the high energy expansion of the connected contribution to the Adler function in the ON shell scheme. 
        In this expresssion the external quark is massive while the inner quarks are consider to be massless. 
        This is obtained from the expansion given in https://arxiv.org/abs/1110.5581. Please note 
        that the URL given in such paper changed. Now it is: https://www.ttp.kit.edu/Progdata/ttp11/ttp11-25/. 
        At order asmu**2 30 terms in the expansion are included. At order asmu**3 only the first term in the expansion. Such term is taken from 
        https://arxiv.org/pdf/2302.01359.pdf  eq.(3.9) specifically from appendix A.17. I converted it to the pole mass. Using the convertion formula. 
        
        
        Parameters
        ----------
        
        m: Pole mass of the external quark. 
        
        Q : float or mp complex number.
            The scale at which the  Adler function wants to be computed. 
        
        mu : float
            Renormalization scale. 
        
        asmu : float
            Strong coupling constant at scale mu. 
        
        nq: number of internal quarks INCLUDING the heavy quark i.e nq=nl+1.
        
        k: number of terms in the m^2/s expansion that are to be included.
        
        nloops : int, optional
            The number of loops at which the Adler function is to be evaluated. nloops=5 is the default value which includes 
            the terms up to order asmu**3; To include only terms up to  order asmu**2 use nloops=2.
        
        Returns
        ----------
        
        If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges.   
        
        IMPORTANT: Only the s supressed terms are included here. The masseless contribution needs to be included through the functions 
        adler_massless_connected and adler_massless_disconnected
        
    """
	npower=k;
	d=0;
	x=(m**2)/(Q**2)
	z=1/x;
	Lz=mp.log(z);
	Lz2=Lz**2;
	Lz3=Lz**3;
	Lq=mp.log(Q**2/mu**2);
	a=asmu/np.pi;
	d0=[-6.,12.*Lz,24. - 24.*Lz,-84. + 72.*Lz,296. - 240.*Lz,-1066. + 840.*Lz,
        3904.8 - 3024.*Lz,-14485.6 + 11088.*Lz,54256.2285714285714285714285714 - 41184.*Lz,
        -204747.857142857142857142857143 + 154440.*Lz,777305.238095238095238095238095 - 583440.*Lz,
        -2.96542870476190476190476190476e6 + 2.217072e6*Lz,1.13591917818181818181818181818e7 - 8.465184e6*Lz,
        -4.3661140496969696969696969697e7 + 3.2449872e7*Lz,1.68311485603729603729603729604e8 - 1.248072e8*Lz,
        -6.50474987328671328671328671329e8 + 4.813992e8*Lz,2.5194490550041958041958041958e9 - 1.86141024e9*Lz,
        -9.77740735564125874125874125874e9 + 7.21296468e9*Lz,3.80092629148425339366515837104e10 - 2.800327464e10*Lz,
        -1.47986659944387631975867269985e11 + 1.089016236e11*Lz,5.76972429720246566642851472573e11 - 4.241431656e11*Lz,
        -2.25231319173696160990712074303e12 + 1.65415834584e12*Lz,8.80224860059575485773256671089e12 - 6.45909449328e12*Lz,
        -3.44354804572597689893182153244e13 + 2.524918756464e13*Lz,1.34842992290466922132114755617e14 - 9.88011687312e13*Lz,
        -5.28478112751312111684116126168e14 + 3.869712441972e14*Lz,2.07287250996657451780173521458e15 - 1.516927277253024e15*Lz,
        -8.13652625885482495445296122642e15 + 5.951022395377248e15*Lz,3.19597259226793738211856996296e16 - 2.3363273107777344e16*Lz,
        -1.25615666311311257726086677116e17 + 9.178428720912528e16*Lz]
	powers = np.arange(1,len(d0[0:npower])+1)
	terms = [d0[i-1] * (x**i) for i in powers]
	d+=sum(terms)
	if(nloops>0):
		d1=[-12. + 12.*Lz, 
			49.7991542344403504661249545017 + 4.*Lz - 24.*Lz2,
			-82.3703703703703703703703703704 - 135.111111111111111111111111111*Lz + 77.3333333333333333333333333333*Lz2,
			40.2407407407407407407407407407 + 572.222222222222222222222222222*Lz - 270.666666666666666666666666667*Lz2,
			332.44 - 2243.76296296296296296296296296*Lz + 1039.11111111111111111111111111*Lz2,
			-2324.67259259259259259259259259 + 8894.48888888888888888888888889*Lz - 4085.33333333333333333333333333*Lz2,
			11730.3720513983371126228269085 - 35523.6368253968253968253968254*Lz + 16205.8666666666666666666666667*Lz2,
			-53629.5790992693373645754598136 + 142430.445502645502645502645503*Lz - 64546.2222222222222222222222222*Lz2,
			234540.361639011865769235383748 - 572167.74270597127739984882842*Lz + 257606.47619047619047619047619*Lz2,
			-1.00121908020870076425631981188e6 + 2.30054795343915343915343915344e6*Lz - 1.02926266666666666666666666667e6*Lz2,
			4.21119021822624420989019353618e6 - 9.25314247268451712896157340602e6*Lz + 4.11502637037037037037037037037e6*Lz2,
			-1.75390028530232094878559525024e7 + 3.72194585907070707070707070707e7*Lz - 1.64582245333333333333333333333e7*Lz2,
			7.25424580606255016073480437399e7 - 1.49694458130750058022785295513e8*Lz + 6.58403670303030303030303030303e7*Lz2,
			-2.98510792700438841028621618402e8 + 6.01950718765501165501165501166e8*Lz - 2.63427708444444444444444444444e8*Lz2,
			1.22358583659909795549437958311e9 - 2.42001865583593386670309747233e9*Lz + 1.05406303917948717948717948718e9*Lz2,
			-5.00011899665916403503881502074e9 + 9.72685593191542161542161542162e9*Lz - 4.21786300666666666666666666667e9*Lz2,
			2.03826162226569155677499703716e10 - 3.90860321322531011181991574148e10*Lz + 1.68783263304888888888888888889e10*Lz2,
			-8.29215258555531294784686680661e10 + 1.57024946776638792362321774086e11*Lz - 6.75415474753333333333333333333e10*Lz2,
			3.36782643136932309309539458787e11 - 6.30693124090628927928071981978e11*Lz + 2.70279587887372549019607843137e11*Lz2,
			-1.36590767493932000192808135999e12 + 2.53264995959691390165721091074e12*Lz - 1.08156703378874074074074074074e12*Lz2,
			5.53314872389845461459600036388e12 - 1.01682322443227083821325959178e13*Lz + 4.32802621505543859649122807018e12*Lz2,
			-2.23910765989532565024172748273e13 + 4.08163859289364390966996539752e13*Lz - 1.73189480607914666666666666667e13*Lz2,
			9.05290611745608589530899123521e13 - 1.63812809138274171182611080309e14*Lz + 6.93023075556200634920634920635e13*Lz2,
			-3.65729378086256729713496523595e14 + 6.573407166867243831155362574e14*Lz - 2.77311645226484606060606060606e14*Lz2,
			1.47649074017406937276188092507e15 - 2.63734779308595341867272048571e15*Lz + 1.10964130132625553623188405797e15*Lz2,
			-5.95709442324276783831462962649e15 + 1.05799341806379208563077305645e16*Lz - 4.44008429213970755555555555556e15*Lz2,
			2.40214814326516805189574490349e16 - 4.24366779873486783484625025317e16*Lz + 1.77661778920611323733333333333e16*Lz2,
			-9.68168905259200823644337332794e16 + 1.70194878505350464550780230632e17*Lz - 7.10871559100496291282051282051e16*Lz2,
			3.90040393290669541103398093429e17 - 6.82498700675746162366573526524e17*Lz + 2.84434847244081419456790123457e17*Lz2,
			-1.57070057487242810862628232732e18 + 2.73659583400480449749331918202e18*Lz - 1.13807060903030115047619047619e18*Lz2]
		powers = np.arange(1,len(d1[0:npower])+1)
		terms = [d1[i-1] * (x**i) for i in powers]
		d+=a*sum(terms)
	if(nloops>1):
		d2=[-46.6149140821436826144498512637 + 33.*Lq + 118.5*Lz - 33.*Lq*Lz + 4.5*Lz2 
			- 0.246402934059572412556327333251*nq - 2.*Lq*nq - 4.33333333333333333333333333333*Lz*nq +  
			2.*Lq*Lz*nq - 1.*Lz2*nq,
			
			715.123856066622412072059025616 - 136.94767414471096378184362488*Lq - 343.1319156733906300387323002*Lz
			- 11.*Lq*Lz - 198.*Lz2 + 66.*Lq*Lz2 - 12.*Lz3 - 51.7087442366650021709424765985*nq +
			8.29985903907339174435415908362*Lq*nq + 24.8745006251271785391141982219*Lz*nq + 
			0.666666666666666666666666666667*Lq*Lz*nq + 8.66666666666666666666666666667*Lz2*nq 
			-4.*Lq*Lz2*nq + 2.66666666666666666666666666667*Lz3*nq,

			-2580.89425590718127108233593598 + 226.518518518518518518518518519*Lq - 57.8884785377679987675376144675*Lz
			+ 371.555555555555555555555555556*Lq*Lz + 801.104938271604938271604938272*Lz2 - 212.666666666666666666666666667*Lq*Lz2 
			- 16.4197530864197530864197530864*Lz3 + 188.709784335814626812885774901*nq - 13.7283950617283950617283950617*Lq*nq -
			10.3642426161222763580833354064*Lz*nq - 22.5185185185185185185185185185*Lq*Lz*nq - 
			15.5555555555555555555555555556*Lz2*nq + 12.8888888888888888888888888889*Lq*Lz2*nq - 9.62962962962962962962962962963*Lz3*nq,

			7958.66598840508604285145183262 - 110.662037037037037037037037037*Lq + 1913.22208272071270881696360972*Lz - 
			1573.61111111111111111111111111*Lq*Lz - 3488.30144032921810699588477366*Lz2 + 744.333333333333333333333333333*Lq*Lz2 +
			79.4485596707818930041152263374*Lz3 - 582.898032188826654842448291467*nq + 6.70679012345679012345679012346*Lq*nq + 
			44.9538840447360190125802552059*Lz*nq + 95.3703703703703703703703703704*Lq*Lz*nq + 43.9074074074074074074074074074*Lz2*nq - 
			45.1111111111111111111111111111*Lq*Lz2*nq + 38.5925925925925925925925925926*Lz3*nq,

			-26265.680661933185924754587248 - 914.21*Lq - 11455.1811319456220653687338047*Lz + 6170.34814814814814814814814815*Lq*Lz +
			14435.3353240740740740740740741*Lz2 - 2857.55555555555555555555555556*Lq*Lz2 - 373.496090534979423868312757202*Lz3 + 
			2064.17473622612038965943544156*nq + 55.4066666666666666666666666667*Lq*nq - 276.837047717264276749948594222*Lz*nq - 
			373.960493827160493827160493827*Lq*Lz*nq - 137.748148148148148148148148148*Lz2*nq + 
			173.185185185185185185185185185*Lq*Lz2*nq -    159.950617283950617283950617284*Lz3*nq,

			88590.3980254773373399676277736 + 6392.84962962962962962962962963*Lq + 56995.3124016606983968409783151*Lz
			- 24459.8444444444444444444444444*Lq*Lz - 58140.9134259259259259259259259*Lz2 + 11234.6666666666666666666666667*Lq*Lz2
			+ 1309.1237037037037037037037037*Lz3 - 7840.79091588707231655326653905*nq - 387.445432098765432098765432099*Lq*nq + 
			1527.77624238781860432509273771*Lz*nq + 1482.41481481481481481481481481*Lq*Lz*nq + 448.259259259259259259259259259*Lz2*nq 
			- 680.888888888888888888888888889*Lq*Lz2*nq + 667.259259259259259259259259259*Lz3*nq,
			
			-279234.268302196336163064170548 - 32258.5231413454270597127739985*Lq - 265321.084389083585067718539863*Lz 
			+ 97690.0012698412698412698412698*Lq*Lz + 218985.722756865709246661627614*Lz2 - 44566.1333333333333333333333333*Lq*Lz2 
			- 1261.41189888300999412110523222*Lz3 + 30908.9473238669561179696065737*nq + 1955.06200856638951877047115142*Lq*nq -
			7701.58437121603894441381479442*Lz*nq - 5920.60613756613756613756613757*Lq*Lz*nq - 1458.62730158730158730158730159*Lz2*nq
			+ 2700.97777777777777777777777778*Lq*Lz2*nq - 2783.58518518518518518518518519*Lz3*nq,

			621604.085778793665679843382511 + 147481.342522990677752582514487*Lq + 1.14840563255557168586135331221e6*Lz
			- 391683.725132275132275132275132*Lq*Lz - 686353.265834101188976472423184*Lz2 + 177502.111111111111111111111111*Lq*Lz2
			- 35088.3395380868396741412614428*Lz3 - 124286.032972518058241265380841*nq - 8938.26318321155622742924330226*Lq*nq +
			36748.1797368998830723020302688*Lz*nq + 23738.4075837742504409171075838*Lq*Lz*nq + 4640.10308641975308641975308642*Lz2*nq - 
			10757.7037037037037037037037037*Lq*Lz2*nq + 11590.691358024691358024691358*Lz3*nq,

			1.39699406547744421588175170092e6 - 644985.99450728263086539730531*Lq - 4.19888910829623561780002940603e6*Lz + 
			1.5734612924414210128495842782e6*Lq*Lz + 779069.963954193236671505756918*Lz2 - 708417.80952380952380952380952*Lq*Lz2 
			+ 496593.074162047535063408079281*Lz3 + 505196.644634058080661704192068*nq + 39090.060273168644294872563958*Lq*nq - 
			169329.04160998050828185000852*Lz*nq - 95361.29045099521289997480474*Lq*Lz*nq - 14092.147140337616528092718569*Lz2*nq 
			+ 42934.412698412698412698412698*Lq*Lz2*nq - 48150.58201058201058201058201*Lz3*nq,
			
			-3.86085060984274393223666207023e7 + 2.75335247057392710170487948266e6*Lq + 6.71040122082061254209354818978e6*Lz -
			6.32650687195767195767195767196e6*Lq*Lz + 1.60392468156941451951477566662e7*Lz2 + 2.83047233333333333333333333333e6*Lq*Lz2 - 
			5.13430272300304209475285313028e6*Lz3 - 2.0657420750524507505374079118e6*nq - 166869.84670145012737605330198*Lq*nq +
			761990.3570202767905359084005*Lz*nq + 383424.65890652557319223985891*Lq*Lz*nq + 39251.564814814814814814814815*Lz2*nq -
			171543.77777777777777777777778*Lq*Lz2*nq + 199560.37037037037037037037037*Lz3*nq,

			4.51962935246239757988478890167e8 - 1.15807731001221715771980322245e7*Lq + 1.08961096186278071836907732059e8*Lz +
			2.54461417998824221046443268665e7*Lq*Lz - 2.51876207995176428186872768746e8*Lz2 - 1.13163225185185185185185185185e7*Lq*Lz2
			+ 4.94533433313805053134859131332e7*Lz3 + 8.4737027082668840678426095072e6*nq + 701865.03637104070164836558936*Lq*nq 
			- 3.3713388365277789348437419582e6*Lz*nq - 1.5421904121140861881602622343e6*Lq*Lz*nq - 90599.086672723709760746797784*Lz2*nq
			+ 685837.7283950617283950617284*Lq*Lz2*nq - 825256.92181069958847736625514*Lz3*nq,

			-4.63385267704654227616706915371e9 + 4.8232257845813826091603869382e7*Lq - 2.05560249268624618165765820079e9*Lz - 
			1.02353511124444444444444444444e8*Lq*Lz + 2.90366184666790809660728936979e9*Lz2 + 4.5260117466666666666666666667e7*Lq*Lz2 - 
			4.7747374817346384896168445952e8*Lz3 - 3.481420264341452535349424737e7*nq - 2.9231671421705349146426587504e6*Lq*nq +
			1.4727796824729520257725280681e7*Lz*nq + 6.2032430984511784511784511785e6*Lq*Lz*nq 
			+ 102936.69428571428571428571429*Lz2*nq - 2.7430374222222222222222222222e6*Lq*Lz2*nq + 3.405866222222222222222222222e6*Lz3*nq,

			4.671730654468170338510030038e10 - 1.9949175966672012942020712028e8*Lq + 2.70244328101164705641010334883e10*Lz 
			+ 4.1165975985956265956265956266e8*Lq*Lz - 3.14832069062673298664904190211e10*Lz2 -
			1.8106100933333333333333333333e8*Lq*Lz2 + 4.75457981479608107211762815418e9*Lz3 +
			1.4312388444475036212443239989e8*nq + 1.209040967677091693455800729e7*Lq*nq - 
			6.370758076695071911887678805e7*Lz*nq - 2.4949076355125009670464215919e7*Lq*Lz*nq +
			606180.2655156291519927883564*Lz2*nq + 1.09733945050505050505050505051e7*Lq*Lz2*nq - 1.4030473131313131313131313131e7*Lz3*nq,

			-4.80343247336991840544065728899e11 + 8.20904679926206812828709450606e8*Lq - 3.26911319866857210355160152581e11*Lz
			- 1.65536447660512820512820512821e9*Lq*Lz + 3.41633598874688489187735649607e11*Lz2 +
			7.24426198222222222222222222222e8*Lq*Lz2 - 4.92601108038124059928100332141e10*Lz3 -
			5.88424455787017971548013057e8*nq - 4.97517987834064735047702697337e7*Lq*nq + 
			2.73417127442482386443047215594e8*Lz*nq + 1.00325119794250194250194250194e8*Lq*Lz*nq - 
			6.42840089838063171396504729838e6*Lz2*nq - 4.39046180740740740740740740741e7*Lq*Lz2*nq + 5.7703298962962962962962962963e7*Lz3*nq,

			5.09367972341779598911787590272e12 - 3.36486105064751937760954385356e9*Lq + 3.88669960764424638611605870047e12*Lz
			+ 6.6550513035488181334335180489e9*Lq*Lz - 3.78334669051564480792243425062e12*Lz2 - 
			2.89867335774358974358974358974e9*Lq*Lz2 + 5.30652337746488681661575434469e11*Lz3 +
			2.41847314496229535850069734986e9*nq + 2.03930972766516325915729930519e8*Lq*nq - 
			1.16591609282208993682142105244e9*Lz*nq - 4.03336442639322311117182912055e8*Lq*Lz*nq +
			4.14862561327823173977020130866e7*Lz2*nq + 1.75677173196581196581196581197e8*Lq*Lz2*nq - 2.36963890917378917378917378917e8*Lz3*nq,

			-5.57717783647683788918768732393e13 + 1.3750327240812701096356741307e10*Lq - 4.64223102761919154899185282194e13*Lz -
			2.67488538127674094424094424094e10*Lq*Lz + 4.29612477170893274038220326679e13*Lz2 + 
			1.15991232683333333333333333333e10*Lq*Lz2 - 5.91764984862988467059789219111e12*Lz3 -
			9.93512478181575853479728866433e9*nq - 8.33353166109860672506469170123e8*Lq*nq + 
			4.94519466630375416255094759223e9*Lz*nq + 1.62114265531923693590360257027e9*Lq*Lz*nq - 
			2.28149792830422619708333994048e8*Lz2*nq - 7.02977167777777777777777777778e8*Lq*Lz2*nq + 9.71803865343915343915343915344e8*Lz3*nq,

			6.28865820315312177057226671738e14 - 5.60521946123065178113124185218e10*Lq + 5.6116196441236847730067899044e14*Lz 
			+ 1.07486588363696028075047682891e11*Lq*Lz - 4.99860982232831018401191940471e14*Lz2 -
			4.64153974088444444444444444444e10*Lq*Lz2 + 6.79663172730035546864097657544e13*Lz3 + 
			4.07881791931108314648933220995e10*nq + 3.39710270377615259462499506193e9*Lq*nq - 
			2.08800938954472138255753136339e10*Lz*nq - 6.51433868870885018636652623581e9*Lq*Lz*nq +
			1.15811455478385562150268032621e9*Lz2*nq + 2.81305438841481481481481481481e9*Lq*Lz2*nq - 3.98056167651358024691358024691e9*Lz3*nq,

			-7.27611040886289167793404451538e15 + 2.28034196102771106065788837182e11*Lq - 6.87871456932540346148691359499e15*Lz 
			- 4.31818603635756678996384878738e11*Lq*Lz + 5.94490544315319978684763365131e15*Lz2 + 
			1.85739255557166666666666666667e11*Lq*Lz2 - 8.00299379965465819046369734144e14*Lz3 -
			1.6733844043130823330211900016e11*nq - 1.38202543092588549130781113443e10*Lq*nq + 
			8.78203842983927818154349664414e10*Lz*nq + 2.61708244627731320603869623477e10*Lq*Lz*nq 
			- 5.60204159667399036149036149036e9*Lz2*nq - 1.12569245792222222222222222222e10*Lq*Lz2*nq + 1.62864780651481481481481481481e10*Lz3*nq,

			8.60879432370603392894864102653e16 - 9.26152268626563850601233511664e11*Lq + 8.54912898115826426069284608594e16*Lz
			+ 1.73440609124922955180219795044e12*Lq*Lz - 7.20803186918714436488045737828e16*Lz2 -
			7.43268866690274509803921568627e11*Lq*Lz2 + 9.62494079207867681516497332046e15*Lz3 + 
			6.86031988037170220980337793149e11*nq + 5.61304405228220515515899097978e10*Lq*nq - 
			3.68125827124153190028797163495e11*Lz*nq - 1.05115520681771487988011996996e11*Lq*Lz*nq
			+ 2.6238966720616211087679551226e10*Lz2*nq + 4.50465979812287581699346405229e10*Lq*Lz2*nq - 6.65685571747799564270152505447e10*Lz3*nq,

			-1.0384954180660445231692981124e18 + 3.75624610608313000530222373997e12*Lq - 1.07635685269558796777121434063e18*Lz
			- 6.96478738889151322955733000453e12*Lq*Lz + 8.88852687220342350568904412707e17*Lz2 + 
			2.97430934291903703703703703704e12*Lq*Lz2 - 1.17879749732678065758191493633e17*Lz3 - 
			2.81045714497472095883543920004e12*nq - 2.27651279156553333654680226665e11*Lq*nq +
			1.53856995944059255266810572456e12*Lz*nq + 4.22108326599485650276201818456e11*Lq*Lz*nq - 
			1.200969541542911815329026658e11*Lz2*nq - 1.8026117229812345679012345679e11*Lq*Lz2*nq + 2.71836228763637860082304526749e11*Lz3*nq,

			1.27416761199960710547626034389e19 - 1.52161589907207501901390010007e13*Lq + 1.37137171633804272805788230208e19*Lz
			+ 2.7962638671887448050864638774e13*Lq*Lz - 1.11251738586439385038597097143e19*Lz2 - 
			1.1902072091402456140350877193e13*Lq*Lz2 + 1.46673401637219106604909227037e18*Lz3 + 
			1.15052618919913808452086506671e13*nq + 9.2219145398307576909933339398e11*Lq*nq - 
			6.41368932616911821818235407101e12*Lz*nq - 1.69470537405378473035543265297e12*Lq*Lz*nq +
			5.40251668980271057454083905662e11*Lz2*nq + 7.21337702509239766081871345029e11*Lq*Lz2*nq 
			- 1.10910980787937621832358674464e12*Lz3*nq,

			-1.58686077045053095262348351516e20 + 6.1575460647121455381647505775e13*Lq - 1.76632798089511517250645549193e20*Lz 
			- 1.12245061304575207515924048432e14*Lq*Lz + 1.4109639545341883998043650506e20*Lz2 +
			4.76271071671765333333333333333e13*Lq*Lz2 - 1.85059407553011494451514603424e19*Lz3 - 
			4.70662860350984469511024514601e13*nq - 3.73184609982554275040287913788e12*Lq*nq +
			2.66742985161863918012283598935e13*Lz*nq + 6.80273098815607318278327566253e12*Lq*Lz*nq 
			- 2.39776018359489249126136639037e12*Lz2*nq - 2.88649134346524444444444444444e12*Lq*Lz2*nq
			+ 4.52168036357665185185185185185e12*Lz3*nq,

			2.0027340575997650135276273382e21 - 2.48954918230042362120997258968e14*Lq + 2.29770627384829888246075140383e21*Lz
			+ 4.50485225130253970752180470851e14*Lq*Lz - 1.81069748247484352850377068892e21*Lz2 - 
			1.90581345777955174603174603175e14*Lq*Lz2 + 2.36399057124651868037574608394e20*Lz3 + 
			1.92409528742529182233301814637e14*nq + 1.5088176862426809825514985392e13*Lq*nq - 
			1.1070762427981977032151971021e14*Lz*nq - 2.73021348563790285304351800515e13*Lq*Lz*nq
			+ 1.05276125137312319117567511357e13*Lz2*nq + 1.15503845926033439153439153439e13*Lq*Lz2*nq - 1.8420828805996218694885361552e13*Lz3*nq,

			-2.55788058415848365274629692208e22 + 1.00575578973720600671211543989e15*Lq - 3.01618264369939936905126931394e22*Lz 
			- 1.80768697088849205356772470785e15*Lq*Lz + 2.34845428570012725015798070253e22*Lz2 +
			7.62607024372832666666666666667e14*Lq*Lz2 - 3.0534875369772312229535859652e21*Lz3 -
			7.86062673109304572307892720188e14*nq - 6.09548963477094549522494205992e13*Lq*nq + 
			4.58617674083145663843018016827e14*Lz*nq + 1.09556786114454063852589376233e14*Lq*Lz*nq - 
			4.58163210499393321453914145536e13*Lz2*nq - 4.62186075377474343434343434343e13*Lq*Lz2*nq + 7.49938401947327542087542087542e13*Lz3*nq,

			3.30219761075830833043917445008e23 - 4.06034953547869077509517254395e15*Lq + 3.99240895723537721748937400764e23*Lz 
			+ 7.2527064309863719013499813357e15*Lq*Lz - 3.07529637236159560732997304976e23*Lz2 - 
			3.05151357864720272463768115942e15*Lq*Lz2 + 3.98374390965524486831005747771e22*Lz3 + 
			3.20932093248340204737212908216e15*nq + 2.46081790029011562126980154179e14*Lq*nq - 
			1.89665945359517604126324055093e15*Lz*nq - 4.39557965514325569778786747618e14*Lq*Lz*nq + 
			1.97932164921025359386114003877e14*Lz2*nq + 1.84940216887709256038647342995e14*Lq*Lz2*nq -
			3.05119429156913455716586151369e14*Lz3*nq,

			-4.30485778909412058187494784273e24 + 1.63820096639176115553652314729e16*Lq - 5.32522494682840222549336329313e24*Lz
			- 2.90948189967542823548462590523e16*Lq*Lz + 4.06242007667989476452397335559e24*Lz2 + 
			1.22102318033841957777777777778e16*Lq*Lz2 - 5.24481030785412845780335647082e23*Lz3 -
			1.30950201249644859572048325622e16*nq - 9.92849070540461306385771604416e14*Lq*nq +
			7.83176127254460801032743412149e15*Lz*nq + 1.76332236343965347605128842741e15*Lq*Lz*nq -
			8.49788842885803802173400994089e14*Lz2*nq - 7.40014048689951259259259259259e14*Lq*Lz2*nq + 1.24068237418080676543209876543e15*Lz3*nq,

			5.66205624407237148821446260663e25 - 6.6059073939792121427132984846e16*Lq + 7.15335976683251579663056286386e25*Lz 
			+ 1.16700864465208865458271881962e17*Lq*Lz - 5.40941542733348127930895840316e25*Lz2 - 
			4.88569892031681140266666666667e16*Lq*Lz2 + 6.96249796536587849873685132186e24*Lz3 +
			5.34008111545361118840173012238e16*nq + 4.00358023877528008649290817248e15*Lq*nq -
			3.2293762024627773593540755013e16*Lz*nq - 7.07277966455811305807708375529e15*Lq*Lz*nq +
			3.62903899926886813262523139698e15*Lz2*nq + 2.96102964867685539555555555556e15*Lq*Lz2*nq -
			5.0421371126234367762962962963e15*Lz3*nq,

			-7.50800339527958579855053310069e26 + 2.66246448946280226502192766518e17*Lq - 
			9.67214927007207906540492943201e26*Lz - 4.68035915889713777514645634237e17*Lq*Lz +
			7.25603795859016412464634784252e26*Lz2 + 1.95489678752636480102564102564e17*Lq*Lz2 -
			9.3131452175526249077768867942e25*Lz3 - 2.17645437969903543855672301225e17*nq - 
			1.61361484209866803940722888799e16*Lq*nq + 1.32989520403824226019570165608e17*Lz*nq + 
			2.83658130842250774251300384386e16*Lq*Lz*nq - 1.54265368205082480973927644606e16*Lz2*nq - 
			1.18478593183416048547008547009e16*Lq*Lz2*nq + 2.04808129637817166267806267806e16*Lz3*nq,

			1.00305598094080915757123594732e28 - 1.07261108154934123803434475693e18*Lq +
			1.31574769617829929619104355213e28*Lz + 1.87687142685830194650807719794e18*Lq*Lz
			- 9.79902657238132335712363591012e27*Lz2 - 7.82195829921223903506172839506e17*Lq*Lz2 
			+ 1.25446953880696742135083647752e27*Lz3 + 8.86588946744596590882086278186e17*nq + 
			6.50067322151115901838996822381e16*Lq*nq - 5.47016255055638237334097317886e17*Lz*nq 
			- 1.13749783445957693727762254421e17*Lq*Lz*nq + 6.53121032662350182326451852458e16*Lz2*nq 
			+ 4.74058078740135699094650205761e16*Lq*Lz2*nq - 8.31518732660670085048010973937e16*Lz3*nq,

			-1.34935267156747506778648424389e29 + 4.31942658089917729872227640014e18*Lq - 1.80001397008844422742608461582e29*Lz 
			- 7.52563854351321236810662775056e18*Lq*Lz + 1.33161869469135432809930635743e29*Lz2 +
			3.12969417483332816380952380952e18*Lq*Lz2 - 1.70068542586474182831538337672e28*Lz3 -
			3.609745997846597228587740382e18*nq - 2.61783429145404684771047054554e17*Lq*nq +
			2.24753490591409515786156856694e18*Lz*nq + 4.56099305667467416248886530337e17*Lq*Lz*nq - 
			2.7553396908118141628897568816e17*Lz2*nq - 1.89678434838383525079365079365e17*Lq*Lz2*nq + 
			3.37444033388315753142857142857e17*Lz3*nq]    
		powers = np.arange(1,len(d2[0:npower])+1)
		terms = [d2[i-1] * (x**i) for i in powers]
		d+=a*a*sum(terms)
	#if(nloops>2):
		# WARNING!!! Care is needed with this terms, please only use it for tails. As one can see from the previous orders the 
		# terms  in the expansion m^n/Q^n have a strong oscilations which cancell each other. 
		#To convince yourself run the following:
		#print(d2[0])
		#print(d2[1])
		#print(d2[2])
		#print(d2[3])
		# I took this terms from https://arxiv.org/pdf/2302.01359.pdf  eq.(3.9) specifically A.17
		#d3=[-3829.2034126333792 + 2861.594707412049*Lq - 776.875*Lq**2 + 71.25*Lq**3 + 365.8721486473844*nq - 247.5951486202796*Lq*nq + 
		#    60.75*Lq**2*nq - 5.666666666666667*Lq**3*nq - 5.236773962019004*nq**2 + 3.759259259259259*Lq*nq**2 - 
		#    1.0555555555555556*Lq**2*nq**2 + 0.1111111111111111*Lq**3*nq**2]
		#powers = np.arange(1,len(d3[0:npower])+1)
        #terms = [d3[i-1] * (x**i) for i in powers]
        #d+=a*sum(terms)
	return 3*d;

def adler_le_o_heavy_i_massless_m_supressed_OS(m,Q,mu,asmu,nq,k,nloops=5):
	"""
        Description
        -----------
        
        Massive contributions to the low energy expansion of the connected contribution to the Adler function in the ON shell scheme. 
        In this expresssion the external quark is massive while the inner quarks are consider to be massless. 
        This is obtained from the expansion given in https://arxiv.org/abs/1110.5581. Please note 
        that the URL given in such paper changed. Now it is: https://www.ttp.kit.edu/Progdata/ttp11/ttp11-25/. 
        At order asmu**2 30 terms in the expansion are included. 
        
        Parameters
        ----------
        
        m: Pole mass of the external quark. 
        
        Q : float or mp complex number.
            The scale at which the  Adler function wants to be computed. 
        
        mu : float
            Renormalization scale. 
        
        asmu : float
            Strong coupling constant at scale mu. 
        
        nq: number of internal quarks INCLUDING the heavy quark i.e nq=nl+1.
        
        k: number of terms in the m^2/s expansion that are to be included.
        
        nloops : int, optional
            The number of loops at which the Adler function is to be evaluated. nloops=5 is the default value which includes 
            the terms up to order asmu**3; To include only terms up to  order asmu**2 use nloops=2.
        
        Returns
        ----------
        
        If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges.   
        
        IMPORTANT: Only the s supressed terms are included here. The masseless contribution needs to be included through the functions 
        adler_massless_connected and adler_massless_disconnected
        
	"""
	npower=k;
	d=0;
	x=(Q**2)/(m**2)
	L=mp.log(mu**2/m**2);
	L2=L**2;
	a=asmu/np.pi;
	d0=[0.2,-0.0428571428571428571428571428571,0.00952380952380952380952380952381,-0.0021645021645021645021645021645,
		0.0004995004995004995004995004995,-0.00011655011655011655011655011655,0.0000274235568353215412038941450706,
		-6.49505293468141765355387646409e-6,1.54644117492414706036997058669e-6,-3.69801150525339514436297314208e-7,
		8.875227612608148346471135541e-8,-2.13662886970196163896527337098e-8,5.15738003031507981819203917133e-9,
		-1.24775323314074511730452560597e-9,3.02485632276544270861703177204e-10,-7.34607964100178943521279144639e-11,
		1.78688423700043526802473305453e-11,-4.35266673115490642211152923539e-12,1.06162603198900156636866566717e-12,
		-2.59234263625221312717929988494e-13,6.33683755528318764421606638542e-14,-1.55050280607992889166988858367e-14,
		3.7971497291753360612323802049e-15,-9.30673953229249034615779461984e-16,2.28278516829815800943493075581e-16,
		-5.60319995855002420497664821881e-17,1.37622455122281296262584342216e-17,-3.38224677842894711153808976633e-18,
		8.31700027482527978247071254017e-19,-2.04624609936177518457612768845e-19]
	powers = np.arange(1,len(d0[0:npower])+1)
	terms = [d0[i-1] * (x**i) for i in powers]
	d+=sum(terms)
	if(nloops>0):
		d1=[1.01234567901234567901234567901,-0.332592592592592592592592592593,0.0944504913076341647770219198791,-0.0254683519498334313149127963943,
			0.00669892473438134126651958026932,-0.00173753631226713699796172878646,0.000446763065286517143302333420857,-0.000114206093116552130817373456319,
			0.0000290748643785523284582304893587,-7.3796835818264039885879773015e-6,1.86881694135375771792650104125e-6,-4.72416764885338891575514463262e-7,
			1.19253655499504592239311394284e-7,-3.00692635462567302694431634952e-8,7.57472370749362380640142839697e-9,-1.90665304505205489902616390089e-9,
			4.79612701494801549825038309615e-10,-1.2057747580117561835452199777e-10,3.02992851602134013431315521698e-11,-7.61056938570674469935121778e-12,
			1.91092435781006724835250782978e-12,-4.79656775029852211768790529413e-13,1.20363417229589533879194519501e-13,-3.01959646467000963842688905956e-14,
			7.57365311894607270800684972775e-15,-1.89921443360010011801034717196e-15,4.76171407184163674428787524522e-16,-1.19366055522086321242527484225e-16,
			2.99180400503541619455639431243e-17,-7.49766362253086896150282748732e-18]
		powers = np.arange(1,len(d1[0:npower])+1)
		terms = [d1[i-1] * (x**i) for i in powers]
		d+=a*sum(terms)
	if(nloops>1):
		d2=[7.39825294163736710071435654851 + 2.78395061728395061728395061728*L - 0.292369809736142125686033956376*nq - 0.168724279835390946502057613169*L*nq,
-3.58477678371519314651958825122 - 0.91462962962962962962962962963*L + 0.135871746794619406011239714402*nq + 0.0554320987654320987654320987654*L*nq,
1.22505492609767846690662232105 + 0.259738851095993953136810279667*L - 0.0444294589560551931102185547345*nq - 0.0157417485512723607961703199798*L*nq,
-0.373361656160120366664678371788 - 0.0700379678620419361160101900843*L + 0.0130538410445183235982177263942*nq + 0.00424472532497223855248546606571*L*nq,
0.107635861918343001397273005759 + 0.0184220430195486884829288457406*L - 0.00364834716598683422239975110177*nq - 0.00111648745573022354441993004489*L*nq,
-0.0300445231382051967834493381467 - 0.00477822485873462674439475416276*L + 0.000991319483168734998968385410303*nq + 0.000289589385377856166326954797743*L*nq,
0.00821332016830965267211716306336 + 0.00122859842953792214408141690736*L - 0.000264616848283240092326236325885*nq - 0.0000744605108810861905503889034761*L*nq,
-0.00221303570935928123263496450266 - 0.000314066756070518359747777004876*L + 0.000069788466770917098138245003794*nq + 0.0000190343488527586884695622427198*L*nq,
0.000590018315601999401078769128898 + 0.0000799558770410189032601338457366*L - 0.0000182472122681925194853143782419*nq - 4.84581072975872140970508155979e-6*L*nq,
-0.000156045687066670735864468225951 - 0.0000202941298500226109686169375791*L + 4.74032121492503174571767488979e-6*nq + 1.22994726363773399809799621692e-6*L*nq,
0.0000410111528771939588235123095549 + 5.13924658872283372429787786343e-6*L - 1.22534878801504202172434163274e-6*nq - 3.11469490225626286321083506875e-7*L*nq,
-0.0000107239320674233698158609518621 - 1.29914610343468195183266477397e-6*L + 3.15503326172828505969618351701e-7*nq + 7.8736127480889815262585743877e-8*L*nq,
2.79256953002894533744013842078e-6 + 3.2794755262363762865810633428e-7*L - 8.09782806699317145328970142707e-8*nq - 1.98756092499174320398852323806e-8*L*nq,
-7.24688244478242264133666943045e-7 - 8.26904747522060082409686996118e-8*L + 2.07299681593700864053692559453e-8*nq + 5.01154392437612171157386058253e-9*L*nq,
1.87511224567514191076804714861e-7 + 2.08304901956074654676039280917e-8*L - 5.29518981149236559545302807157e-9*nq - 1.26245395124893730106690473283e-9*L*nq,
-4.83965836141819545146943233525e-8 - 5.24329587389315097232195072745e-9*L + 1.35009183099453499705001015834e-9*nq + 3.17775507508675816504360650148e-10*L*nq,
1.24640692087557464003128535243e-8 + 1.31893492911070426201885535144e-9*L - 3.43684397667577215930106749755e-10*nq - 7.99354502491335916375063849359e-11*L*nq,
-3.20392041216134810858213572196e-9 - 3.31588058453232950474935493867e-10*L + 8.73703999843849657635677895434e-11*nq + 2.00962459668626030590869996283e-11*L*nq,
8.22201643035604042032569015672e-10 + 8.33230341905868536936117684669e-11*L - 2.21846670738660186931114546806e-11*nq - 5.04988086003556689052192536163e-12*L*nq,
-2.10683917845846174078671625457e-10 - 2.0929065810693547923215848895e-11*L + 5.62714864364926689223082546344e-12*nq + 1.26842823095112411655853629667e-12*L*nq,
5.39149970829008812068963658315e-11 + 5.25504198397768493296939653188e-12*L - 1.42601177041516471288750019214e-12*nq - 3.18487392968344541392084638296e-13*L*nq,
-1.37807008986896171931331950433e-11 - 1.31905613133209358236417395588e-12*L + 3.61078120122372566473515041689e-13*nq + 7.99427958383087019614650882354e-14*L*nq,
3.51857262002698122585614639839e-12 + 3.30999397381371218167784928628e-13*L - 9.13608237361206364885982843727e-14*nq - 2.00605695382649223131990865835e-14*L*nq,
-8.97507991535193696984692151465e-13 - 8.30389027784252650567394491379e-14*L + 2.31010456000294992412681090291e-14*nq + 5.03266077445001606404481509927e-15*L*nq,
2.28730538027088970676792189737e-13 + 2.08275460771016999470188367513e-14*L - 5.83772533601591399827390225492e-15*nq - 1.26227551982434545133447495462e-15*L*nq,
-5.82447390656651253761920870968e-14 - 5.22283969240027532452845472288e-15*L + 1.47441586085621275499233000119e-15*nq + 3.16535738933350019668391195326e-16*L*nq,
1.48205635712470508454212585892e-14 + 1.30947136975645010467916569243e-15*L - 3.72204412304030899480144385983e-16*nq - 7.93619011973606124047979207536e-17*L*nq,
-3.76854390221115224009217861573e-15 - 3.28256652685737383416950581618e-16*L + 9.39175015478170557727196076102e-17*nq + 1.98943425870143868737545807041e-17*L*nq,
9.57647800222575257224226398093e-16 + 8.22746101384739453503008435917e-17*L - 2.36881513061422306157516554001e-17*nq - 4.98634000839236032426065718738e-18*L*nq,
-2.4321004858908770182314643991e-16 - 2.06185749619598896441327755901e-17*L + 5.97241142862680784019809922152e-18*nq + 1.24961060375514482691713791455e-18*L*nq]    
		powers = np.arange(1,len(d2[0:npower])+1)
		terms = [d2[i-1] * (x**i) for i in powers]
		d+=a*a*sum(terms)
	if(nloops>2):
		# WARNING!!! Care is needed with this terms, please only use it for tails. As one can see from the previous orders the 
		# terms  in the expansion m^n/Q^n have a strong oscilations which cancell each other. 
		#To convince yourself run the following:
		#print(d2[0])
		#print(d2[1])
		#print(d2[2])
		#print(d2[3])
		# I took this terms from https://arxiv.org/pdf/0907.2117.pdf source code in https://www.ttp.kit.edu/Progdata/ttp09/ttp09-18/
		d3=[117.85663562453816 + 47.14409488270922*L + 7.655864197530866*L2 - 13.416097416192219*nq -
			4.8755585966460115*L*nq - 0.9279835390946504*L2*nq + 0.2790953122137951*nq**2 + 
			0.0974566032453807*L*nq**2 + 0.028120713305898496*L2*nq**2,
			
			-57.0714955086514 - 21.836550088211343*L - 2.5152314814814813*L2 + 5.767832175973426*nq +
			2.20552267107794*L*nq + 0.30487654320987656*L2*nq - 0.11039461548335683*nq**2 - 
			0.04529058226487313*L*nq**2 - 0.009238683127572016*L2*nq**2,
			
			20.8042498078054 + 7.339923975623426*L + 0.7142818405139835*L2 - 1.9588430145288616*nq - 
			0.7274869719094069*L*nq - 0.086579617031998*L2*nq + 0.03590456300997034*nq**2 + 0.0148098196520184*L*nq**2
			+ 0.0026236247585453938*L2*nq**2]
		powers = np.arange(1,len(d3[0:npower])+1)
		terms = [d3[i-1] * (x**i) for i in powers]
		d+=a*a*a*sum(terms)
	return 3*d;


def adler_le_o_heavy_i_massless_m_supressed_MS(m,Q,mu,asmu,nq,k,nloops=5):
	"""
        Description
        -----------
        
        Massive contributions to the low energy expansion of the connected contribution to the Adler function in the MSbar scheme. 
        In this expresssion the external quark is massive while the inner quarks are consider to be massless. 
        This is obtained from the expansion given in https://arxiv.org/abs/1110.5581. Please note 
        that the URL given in such paper changed. Now it is: https://www.ttp.kit.edu/Progdata/ttp11/ttp11-25/. 
        At order asmu**2 30 terms in the expansion are included. At order asmu**3 3 terms in the expansion are included. Obtained from https://arxiv.org/pdf/0907.2117.pdf
        
        Parameters
        ----------
        
        m: Pole mass of the external quark. 
        
        Q : float or mp complex number.
            The scale at which the  Adler function wants to be computed. 
        
        mu : float
            Renormalization scale. 
        
        asmu : float
            Strong coupling constant at scale mu. 
        
        nq: number of internal quarks INCLUDING the heavy quark i.e nq=nl+1.
        
        k: number of terms in the m^2/s expansion that are to be included.
        
        nloops : int, optional
            The number of loops at which the Adler function is to be evaluated. nloops=5 is the default value which includes 
            the terms up to order asmu**3; To include only terms up to  order asmu**2 use nloops=2.
        
        Returns
        ----------
        
        If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges.   
        
        IMPORTANT: Only the s supressed terms are included here. The masseless contribution needs to be included through the functions 
        adler_massless_connected and adler_massless_disconnected
        
	"""
	npower=k;
	d=0;
	x=(Q**2)/(m**2)
	L=mp.log(mu**2/m**2);
	L2=L**2;
	a=asmu/np.pi;
	d0=[0.2,-0.0428571428571428571428571428571,0.00952380952380952380952380952381,-0.0021645021645021645021645021645,
		0.0004995004995004995004995004995,-0.00011655011655011655011655011655,0.0000274235568353215412038941450706,
		-6.49505293468141765355387646409e-6,1.54644117492414706036997058669e-6,-3.69801150525339514436297314208e-7,
		8.875227612608148346471135541e-8,-2.13662886970196163896527337098e-8,5.15738003031507981819203917133e-9,
		-1.24775323314074511730452560597e-9,3.02485632276544270861703177204e-10,-7.34607964100178943521279144639e-11,
		1.78688423700043526802473305453e-11,-4.35266673115490642211152923539e-12,1.06162603198900156636866566717e-12,
		-2.59234263625221312717929988494e-13,6.33683755528318764421606638542e-14,-1.55050280607992889166988858367e-14,
		3.7971497291753360612323802049e-15,-9.30673953229249034615779461984e-16,2.28278516829815800943493075581e-16,
		-5.60319995855002420497664821881e-17,1.37622455122281296262584342216e-17,-3.38224677842894711153808976633e-18,
		8.31700027482527978247071254017e-19,-2.04624609936177518457612768845e-19]
	powers = np.arange(1,len(d0[0:npower])+1)
	terms = [d0[i-1] * (x**i) for i in powers]
	d+=sum(terms)
	if(nloops>0):
		d1=[0.479012345679012345679012345679 - 0.4*L,-0.104021164021164021164021164021 + 0.171428571428571428571428571429*L,
			0.0182600151171579743008314436886 - 0.0571428571428571428571428571429*L,
			-0.00238032886181034329182477330625 + 0.017316017316017316017316017316*L,
			0.0000389180743746812598595736093159 - 0.004995004995004995004995004995*L,
			0.000127265552534727803903073078342 + 0.0013986013986013986013986013986*L,
			-0.0000651433289728182925036906204613 - 0.000383929795694501576854518030989*L,
			0.0000243550361566514457917759082488 + 0.000103920846954902682456862023425*L,
			-8.03972381962720099064880472178e-6 - 0.0000278359411486346470866594705604*L,
			2.48168043218264972971328441072e-6 + 7.39602301050679028872594628416e-6*L,
			-7.34583158344632463705032050778e-7 - 1.95255007477379263622364981902e-6*L,
			2.11304473419288832893373015452e-7 + 5.12790928728470793351665609035e-7*L,
			-5.95355188847515081246792969894e-8 - 1.34091880788192075272993018455e-7*L,
			1.65135238243310874432591257943e-8 + 3.49370905279408632845267169671e-8*L,
			-4.5247015835681470280666986912e-9 - 9.07456896829632812585109531613e-9*L,
			1.22767426844204192666462711624e-9 + 2.35074548512057261926809326284e-9*L,
			-3.3044148594539577167950734177e-10 - 6.07540640580147991128409238539e-10*L,
			8.83505272942598899068314055289e-11 + 1.56696002321576631196015052474e-10*L,
			-2.34897671272293446862141749667e-11 - 4.03417892155820595220092953524e-11*L,
			6.21525800763839197893838160637e-12 + 1.03693705450088525087171995398e-11*L,
			-1.63770467314851783240848934606e-12 - 2.66147177321893881057074788188e-12*L,
			4.29971537870372738010877439672e-13 + 6.82221234675168712334750976813e-13*L,
			-1.12528432826497744543058133066e-13 - 1.74668887542065458816689489425e-13*L,
			2.93671683599718418311409949714e-14 + 4.46723497550039536615574141753e-14*L,
			-7.64491466970831402155935531099e-15 - 1.14139258414907900471746537791e-14*L,
			1.98567087099458333077346225975e-15 + 2.91366397844601258658785707378e-15*L,
			-5.14710269696261658661819739436e-16 - 7.43161257660318999817955447968e-16*L,
			1.33175037267275063085649884995e-16 + 1.89405819592021038246133026915e-16*L,
			-3.44000954082946683722095671864e-17 - 4.8238601593986622738330132733e-17*L,
			8.87230517236333251510619402031e-18 + 1.22774765961706511074567661307e-17*L]
		powers = np.arange(1,len(d1[0:npower])+1)
		terms = [d1[i-1] * (x**i) for i in powers]
		d+=a*sum(terms)
	if(nloops>1):
		d2=[-0.0285741363035760558816137249117 - 0.524074074074074074074074074074*L - 0.15*L2 + 0.124176954732510288065843621399*nq - 0.0242798353909465020576131687243*L*nq + 0.0333333333333333333333333333333*L2*nq,
-0.0897521277369758854035022257538 + 0.508597883597883597883597883598*L - 0.107142857142857142857142857143*L2 - 0.0426482951205173427395649617872*nq - 0.00647266313932980599647266313933*L*nq - 0.0142857142857142857142857142857*L2*nq,
-0.00269420127088996421538535805158 - 0.185535525321239606953892668178*L + 0.0928571428571428571428571428571*L2 + 0.0150772216823237231400496706619*nq + 0.00489317208364827412446460065508*L*nq + 0.0047619047619047619047619047619*L2*nq,
0.0105910359472524539077990377767 + 0.0507362647640425418203195980974*L - 0.0454545454545454545454545454545*L2 - 0.00497848642165710556853022069561*nq - 0.00200828092803401445376754018729*L*nq - 0.001443001443001443001443001443*L2*nq,
-0.00519455007616683480515511434396 - 0.0113127920698524697700125446982*L + 0.0181068931068931068931068931069*L2 + 0.00155328575694838572954677209722*nq + 0.000687264348021580207383821758865*L*nq + 0.00041625041625041625041625041625*L2*nq,
0.00185285172177225552312536057359 + 0.00191137172763185639198515211391*L - 0.00646853146853146853146853146853*L2 - 0.000465137735253126587576641085414*nq - 0.000215461119672648884178095707307*L*nq - 0.00011655011655011655011655011655*L2*nq,
-0.000568325271591820965875588226113 - 0.000114982514547818524887207838244*L + 0.00215960510078157136980666392431*L2 + 0.000135194937165898382411614084704*nq + 0.0000641808042308171566470759410475*L*nq + 0.0000319941496412084647378765025824*L2*nq,
0.000158270335068007055001948682933 - 0.000093212358716888232982127149232*L - 0.000688475611076230271276710905194*L2 - 0.0000384312646288497070539551073429*nq - 0.0000184926236587339468620823768506*L*nq - 8.66007057957522353807183528546e-6*L2*nq,
-0.0000408573274055523912189626955427 + 0.0000611347515460799694576879411863*L + 0.000212249051258339184035778463023*L2 + 0.0000107402157853164461911677943841*nq + 5.20605690724823448269972725369e-6*L*nq + 2.31966176238622059055495588003e-6*L2*nq,
9.81642061227383516096892797338e-6 - 0.000026476103306948212616617691374*L - 0.0000637906984656210662402612867009*L2 - 2.96165242248073208136696034899e-6*nq - 1.44083882348971805060859549681e-6*L*nq - 6.16335250875565857393828857014e-7*L2*nq,
-2.17090128076856333121239196589e-6 + 9.8288443830087161879946402938e-6*L + 0.0000187932944696977541236526295081*L2 + 8.07972252260079628626002070295e-7*nq + 3.93618036776021054537456705549e-7*L*nq + 1.62712506231149386351970818252e-7*L2*nq,
4.25705594547361888168348991501e-7 - 3.35780675921784803033258169173e-6*L - 5.448403617740002179361447096e-6*L2 - 2.18500179353971119374916358188e-7*nq - 1.06438374559946860114404614941e-7*L*nq - 4.27325773940392327793054674196e-8*L2*nq,
-6.56411910197854183211525003296e-8 + 1.08808124399654839767093407258e-6*L + 1.55881811416273287504854383954e-6*L2 + 5.86605670396624403704152230852e-8*nq + 2.85464588124852618086955798391e-8*L*nq + 1.11743233990160062727494182046e-8*L2*nq,
3.35252083045604529580927842448e-9 - 3.39813734981823884855629759669e-7*L - 4.4108076791525339896714980171e-7*L2 - 1.56523618890353385694391433658e-8*nq - 7.60462765515807891894967610003e-9*L*nq - 2.91142421066173860704389308059e-9*L2*nq,
3.13408325798656633070557068902e-9 + 1.03258445013910948570229703845e-7*L + 1.23641002193037470714721173682e-7*L2 + 4.15476604523631621618551720404e-9*nq + 2.01447373174695896660154635355e-9*L*nq + 7.56214080691360677154257943011e-10*L2*nq,
-1.95126296837127752641197897949e-9 - 3.07182427389551284873899705278e-8*L - 3.43796527198883745567958639691e-8*L2 - 1.09789673379613305320302252258e-9*nq - 5.31104806562642073786895250323e-10*L*nq - 1.9589545709338105160567443857e-10*L2*nq,
8.22808820794748248689023280238e-10 + 8.98464418784579105124270069521e-9*L + 9.49282250906481236138139435218e-9*L2 + 2.88988322624605574084612845145e-10*nq + 1.39454225515919849603308062314e-10*L*nq + 5.06283867150123325940341032116e-11*L2*nq,
-3.00054500375711669826103076253e-10 - 2.59161802740732627884427765962e-9*L - 2.60507103859621149363375024738e-9*L2 - 7.58076319461780162764277620824e-11*nq - 3.64884215381511804283628804318e-11*L*nq - 1.30580001934647192663345877062e-11*L2*nq,
1.01211958493049672249500741614e-10 + 7.38926173383757352077945807006e-10*L + 7.11024034924633799075413830585e-10*L2 + 1.98259373527016867101394325943e-11*nq + 9.5179874678135101590925424045e-12*L*nq + 3.36181576796517162683410794603e-12*L2*nq,
-3.24949561461598246192205259853e-11 - 2.08619334164302218592037565854e-10*L - 1.93129526400789877974857841428e-10*L2 - 5.17117073160069410493280529266e-12*nq - 2.47606668807985040047823020381e-12*L*nq - 8.64114212084071042393099961648e-13*L2*nq,
1.00798102860147264855859225671e-11 + 5.84024915885541683820228052603e-11*L + 5.22313835494216741574509271818e-11*L2 + 1.34555686923232527638449836859e-12*nq + 6.42599636249605584647352096826e-13*L*nq + 2.2178931443491156754756232349e-13*L2*nq,
-3.0478731380908017866659052951e-12 - 1.62297540439118778698761193127e-11*L - 1.40708129651753546919042388968e-11*L2 - 3.49364499767004300077463312785e-13*nq - 1.66414872238835555270528320058e-13*L*nq - 5.68517695562640593612292480678e-14*L2*nq,
9.03523529486655623777177613924e-13 + 4.48112759309063289660040829928e-12*L + 3.77721469309716554691091020882e-12*L2 + 9.053357616134505476193049655e-14*nq + 4.301430651859204892616100682e-14*L*nq + 1.45557406285054549013907907854e-14*L2*nq,
-2.63626859333757225000510932126e-13 - 1.23021292924642544518985739949e-12*L - 1.01071191320696445159273649572e-12*L2 - 2.34192612791177363726778707465e-14*nq - 1.10990210815236338692953622418e-14*L*nq - 3.72269581291699613846311784794e-15*L2*nq,
7.59236222793106889569002517935e-14 + 3.36016465243759009497835511349e-13*L + 2.6965399800521991486450119553e-13*L2 + 6.04835936187940956661009415002e-15*nq + 2.85941992293621762125637224337e-15*L*nq + 9.51160486790899170597887814921e-16*L2*nq,
-2.16280864191792826291342206552e-14 - 9.13599491107482845785448319214e-14*L - 7.17489754692330599447259804418e-14*L2 - 1.559777396570157115025330172e-15*nq - 7.35620697727710081043890525761e-16*L*nq - 2.42805331537167715548988089482e-16*L2*nq,
6.10403559334994900761086797162e-15 + 2.47377535446002055484869433652e-14*L + 1.90435072275456743703351083542e-14*L2 + 4.01699131088120119998044241186e-16*nq + 1.89001886291087915307241546568e-16*L*nq + 6.19301048050265833181629539974e-17*L2*nq,
-1.70894150977349836136848619557e-15 - 6.67329954955001731651731260821e-15*L - 5.0429299466375601433032918416e-15*L2 - 1.03323451758657089806781072007e-16*nq - 4.85022033767709880484601234595e-17*L*nq - 1.57838182993350865205110855762e-17*L2*nq,
4.75107978052649972869640572632e-16 + 1.79407835945489330235076621059e-15*L + 1.33259136903388045314636991675e-15*L2 + 2.65459322350265359691914333784e-17*nq + 1.24331550116583645534696685217e-17*L*nq + 4.01988346616555189486084439441e-18*L2*nq,
-1.31272682314851726848523175956e-16 - 4.80826710301257265294195915791e-16*L - 3.51442767565384887950949930492e-16*L2 - 6.81294645130941354020613519664e-18*nq - 3.18392261152870140633113874376e-18*L*nq - 1.02312304968088759228806384423e-18*L2*nq]    
		powers = np.arange(1,len(d2[0:npower])+1)
		terms = [d2[i-1] * (x**i) for i in powers]
		d+=a*a*sum(terms)
	if(nloops>2):
		# WARNING!!! Care is needed with this terms, please only use it for tails. As one can see from the previous orders the 
		# terms  in the expansion m^n/Q^n have a strong oscilations which cancell each other. 
		#To convince yourself run the following:
		#print(d2[0])
		#print(d2[1])
		#print(d2[2])
		#print(d2[3])
		# I took this terms from https://arxiv.org/pdf/0907.2117.pdf source code in https://www.ttp.kit.edu/Progdata/ttp09/ttp09-18/
		d3=[0.894308644665812379792799805297 - 4.4694282013423515865321500948*L - 0.175*L**3 - 0.208796296296296296296296296296*L2
			- 0.560048373519998592916016200052*nq + 1.04908208860020630031737792648*L*nq + 0.0555555555555555555555555555556*L**3*nq
			+ 0.080967078189300411522633744856*L2*nq + 0.0180190125811775680699602312839*nq**2 - 
			0.0305898491083676268861454046639*L*nq**2 - 0.0037037037037037037037037037037*L**3*nq**2 + 0.00404663923182441700960219478738*L2*nq**2,

			0.676161760544130263678372739758 + 1.83874261968201412603936747266*L - 0.05357142857142857142857142857*L**3 - 
			0.300694444444444444444444444444*L2 - 0.093136973462398069829178866886*nq - 
			0.340493824832990055454644686211*L*nq + 0.0047619047619047619047619047619*L**3*nq -
			0.0812874779541446208112874779541*L2*nq + 0.00149522721633640184812795888341*nq**2 + 
			0.0095864687438761512835586909661*L*nq**2 + 0.0015873015873015873015873015873*L**3*nq**2 + 0.00107877718988830099941211052322*L2*nq**2,

			-0.361810652119347645020015099786 - 0.606465824534623045103191674716*L - 0.01547619047619047619047619048*L**3 + 
			0.399955309901738473167044595616*L2 + 0.0710642765206375585239254024483*nq +
			0.0989821583648222005608659031996*L*nq - 0.011111111111111111111111111111*L**3*nq +
			0.0189850088183421516754850088183*L2*nq - 0.00139205122326073388560384847226*nq**2 - 
			0.00348253068423136450347334701076*L*nq**2 - 0.0005291005291005291005291005291*L**3*nq**2 - 0.000815528680608045687410766775846*L2*nq**2]
		powers = np.arange(1,len(d3[0:npower])+1)
		terms = [d3[i-1] * (x**i) for i in powers]
		d+=a*a*a*sum(terms)
	return 3*d;



def adler_o_masless_i_heavy(m,Q,cut=None):
    """
        Description
        -----------
        
        Double bubble contributions where the external quark is massless, while the internal is massive. Converted from the results in  
        https://arxiv.org/pdf/hep-ph/9407338.pdf. For steps of the derivation, see https://arxiv.org/pdf/2302.01359.pdf.
        
        
        Parameters
        ----------
        
        m: MSbar or polle mass of the internal quark. 
        
        Q : float or mp complex number.
            The scale at which the Adler function wants to be computed. 
        
        cut : float
           The point at which we switch the Q/m for the m/Q expansion. The default value is 2*m; 
        
        Returns
        ----------
        
        If complex number was used as input, returns a complex number. If positive real, returns a real number. 
        
        IMPORTANT: It is still necessary to muliply this expression by the sum of the squared charges and by $(\\alpha_s/\pi)^2$.   
        
        IMPORTANT: Only the mass and s suppresed terms are included here. The masseless contribution needs to be included through the functions 
        adler_massless_connected and adler_massless_disconnected.
        
    """
    if(cut==None):
        cut=2*m;   
    if(Q<=cut):
        Q2=Q*Q;
        m2=m*m;
        x=Q2/m2
        L=mp.log(x);
        L2=L**2;
        vec=[0.10770104333270812 - 0.05037037037037037*L + 0.007407407407407408*L2,
            0.0027925936362302103- 0.002065381708238851*L + 0.0003968253968253968*L2,
            0.00017956121766281785 - 0.00016046583242350436*L+0.00003527336860670194*L2,
            0.000022488275883643888  - 0.000016752883515750278*L + 4.008337341670675e-6*L2,
            7.931461996570546e-7  - 2.0823529061323013e-6*L + 5.285719571433857e-7*L2,
            6.473976407411328e-7  - 2.906456984786063e-7*L + 7.708341041674375e-8*L2]
        powers = np.arange(1,len(vec)+1)
        terms = vec * (x ** powers)
        return 3*np.sum(terms)
    else:
        Q2=Q*Q;
        m2=m*m;
        x=m2/Q2
        L=mp.log(x);
        L2=L**2;
        L3=L**3;
        vec=[1.0494541744412267 ,
            -3.5678515733249867 - 1.949788558610087*L - 1.*L2,
            -1.7224794272302404 - 2.3703703703703702*L - 0.7407407407407407*L2 +  0.2962962962962963*L3,
            0.23557864742109302 - 4.2407407407407405*L + 0.05555555555555555*L2 + 0.2222222222222222*L3,
            -6.223857120213552 - 5.337283950617284*L + 0.4*L2 + 0.2962962962962963*L3]
        powers = np.arange(1,len(vec)+1)
        terms = vec * (x ** powers)
        return 3*np.sum(terms)



    
def adler_db_heavy(Q,m1,m2,cut_low,cut_high):
    if(Q>2*m2):
        return adler_o_masless_i_heavy(m2,Q,cut=None)
    if(Q>2*m1): 
        return adler_o_masless_i_heavy(m2,Q,cut=None)+8/(5.*(4*m2**2 + Q**2))*m1**2;
    else: 
        return 0