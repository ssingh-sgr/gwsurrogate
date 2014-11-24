""" Gravitational Wave Surrogate classes for text and hdf5 files"""

from __future__ import division

__copyright__ = "Copyright (C) 2014 Scott Field and Chad Galley"
__email__     = "sfield@astro.cornell.edu, crgalley@tapir.caltech.edu"
__status__    = "testing"
__author__    = "Scott Field, Chad Galley"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import numpy as np
from scipy.interpolate import splrep
from scipy.interpolate import splev
import const_mks as mks
import gwtools
import matplotlib.pyplot as plt
import time
import os as os
from parametric_funcs import function_dict as my_funcs
from surrogateIO import TextSurrogateRead, TextSurrogateWrite

try:
	import h5py
	h5py_enabled = True
except ImportError:
	h5py_enabled = False


# needed to search for single mode surrogate directories 
def list_folders(path,prefix):
        '''returns all folders which begin with some prefix'''
        for f in os.listdir(path):
                if f.startswith(prefix):
                        yield f


##############################################
class H5Surrogate:
	"""Load or export a single-mode surrogate in terms of the function's amplitude and phase from HDF5 data format"""

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def __init__(self, file=None, mode=None):
		
		### Make list of required data for reading/writing surrogate data ###
		self.required = ['tmin', 'tmax', 'greedy_points', 'eim_indices', 'B', \
						'affine_map', 'fitparams_amp', 'fitparams_phase', \
						'fit_min', 'fit_max', 'fit_type_amp', 'fit_type_phase']
		
		### Check file mode if specified ###
		if mode is not None:
			if mode in ['r', 'w', 'r+', 'a']:
				self.mode = mode
			else:
				raise Exception, "File mode not recognized. Must be 'r', 'w', 'r+', 'a'."
		
		### Check if file is a pointer or path name (string) and open if in 'r' mode ###
		if file is not None:
			self.type = type(file)
			if self.type == str:
				if mode == 'r':
					try:
						self.file = h5py.File(file, 'r')
					except:
						pass
				if mode == 'w':
					self.file = h5py.File(file, 'w')
			elif self.type == h5py._hl.files.File:
				if mode == 'r' or mode == 'w':
					self.file = file
		
			#if file is not None:
			
			### If mode is 'r' then import surrogate data ###
			if mode == 'r':
				
				self.load_h5(file)
				
#				### Get data keys listing all available surrogate data ###
#				self.keys = self.file.keys()
#					
#				### Get SurrogateID ####
#				#if self.type == str:
#				name = self.file.filename.split('.')[0]
#				if 'surrogate_ID' in self.keys:
#					self.surrogate_ID = self.chars_to_string(self.file['surrogate_ID'][()])
#					if self.surrogate_ID != name:
#						print "\n>>> Warning: SurrogateID does not have expected name."
#				else:
#					"\n>>> Warning: No surrogate ID found."
#			
#				### Unpack time info ###
#				self.tmin = self.file['tmin'][()]
#				self.tmax = self.file['tmax'][()]
#				
#				if 'times' in self.keys:
#					self.times = self.file['times'][:]
#				
#				if 'quadrature_weights' in self.keys:
#					self.quadrature_weights = self.file['quadrature_weights'][:]
#				
#				if 'dt' in self.keys:
#					self.dt = self.file['dt'][()]
#					self.times = np.arange(self.tmin, self.tmax+self.dt, self.dt)
#					self.quadrature_weights = self.dt * np.ones(self.times.shape)
#				
#				if 'times' not in self.__dict__.keys():
#					print "\n>>> Warning: No time samples found or generated."
#				
#				if 'quadrature_weights' not in self.__dict__.keys():
#					print "\n>>> Warning: No quadrature weights found or generated."
#				
#				if 't_units' in self.keys:
#					self.t_units = self.file['t_units'][()]
#				else:
#					self.t_units = 'TOverMtot'
#				
#				### Greedy points (ordered by RB selection) ###
#				self.greedy_points = self.file['greedy_points'][:]
#				
#				### Empirical time index (ordered by EIM selection) ###
#				self.eim_indices = self.file['eim_indices'][:]
#				
#				### Complex B coefficients ###
#				self.B = self.file['B'][:]	
#				
#				### Information about phase/amp parametric fit ###
#				self.affine_map = self.file['affine_map'][()]
#				self.fitparams_amp = self.file['fitparams_amp'][:]
#				self.fitparams_phase = self.file['fitparams_phase'][:]
#				self.fit_min = self.file['fit_min'][()]
#				self.fit_max = self.file['fit_max'][()]
#				self.fit_interval = [self.fit_min, self.fit_max]
#				
#				self.fit_type_amp = self.chars_to_string(self.file['fit_type_amp'][()])
#				self.fit_type_phase = self.chars_to_string(self.file['fit_type_phase'][()])
#				
#				self.amp_fit_func   = my_funcs[self.fit_type_amp]
#				self.phase_fit_func = my_funcs[self.fit_type_phase]
#				
#				if 'fit_type_norm' in self.keys:
#					self.fitparams_norm = self.file['fitparams_norm'][:]
#					self.fit_type_norm = self.chars_to_string(self.file['fit_type_norm'][()])
#					self.norm_fit_func  = my_funcs[self.fit_type_norm]
#					self.norms = True
#			
#				else:
#					self.norms = False
#				
#				if 'eim_amp' in self.keys:
#					self.eim_amp = self.file['eim_amp'][:]
#			
#				if 'eim_phase' in self.keys:
#					self.eim_phase = self.file['eim_phase'][:]
#							
#				### Transpose matrices if surrogate was built using ROMpy ###
#				Bshape = np.shape(self.B)
#			
#				if Bshape[0] < Bshape[1]:
#					transposeB = True
#					self.B = np.transpose(self.B)
#					self.dim_rb = Bshape[0]
#					self.time_samples = Bshape[1]
#			
#				else:
#					self.dim_rb = Bshape[1]
#					self.time_samples = Bshape[0]
#				
#				### Vandermonde V such that E (orthogonal basis) is E = BV ###
#				if 'V' in self.keys:
#					self.V = file['V'][:]
#					if transposeB:
#						self.V = np.transpose(self.V)
#	
#				### R matrix such that waveform basis H = ER ###
#				if 'R' in self.keys:
#					self.R = file['R'][:]
#					if transposeB:
#						self.R = np.transpose(self.R)
#				
#				self.file.close()
			
		pass
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def chars_to_string(self, chars):
		return "".join(chr(cc) for cc in chars)

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def string_to_chars(self, string):
		return [ord(cc) for cc in string]
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def print_required(self):
		""" Print variable names required for importing and exporting surrogate data"""
		
		print "\nGWSurrogate requires data for the following:"
		
		for kk in self.required:
			print "\t"+kk
		
		pass
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def check_required(self, dict):
		""" Check if input dictionary has the minimum required surrogate data"""
		keys = dict.keys()
		
		for kk in self.required:
			if kk not in keys:
				raise Exception, "\nGWSurrogate requires data for "+kk
		
		return keys
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def prepare_data(self, dataclass):
		""" Prepare a dictionary to export with entries filled from imported surrogate data"""
		dict = {}

		for kk in dataclass.keys:
			dict[kk] = dataclass.__dict__[kk]
		
		return dict
			
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def load_h5(self, file):
		
		#if path is not None:
		#	file = h5py.File(path, 'r')
		#else:
		#	file = self.file
		
		self.type = type(file)
		if self.type == str:
			try:
				self.file = h5py.File(file, 'r')
			except:
				pass
		elif self.type == h5py._hl.files.File:
			self.file = file
		
		### Get data keys listing all available surrogate data ###
		self.keys = self.file.keys()
			
		### Get SurrogateID ####
		#if self.type == str:
		name = self.file.filename.split('.')[0]
		if 'surrogate_ID' in self.keys:
			self.surrogate_ID = self.chars_to_string(self.file['surrogate_ID'][()])
			if self.surrogate_ID != name:
				print "\n>>> Warning: SurrogateID does not have expected name."
		else:
			"\n>>> Warning: No surrogate ID found."
	
		### Unpack time info ###
		self.tmin = self.file['tmin'][()]
		self.tmax = self.file['tmax'][()]
		
		if 'times' in self.keys:
			self.times = self.file['times'][:]
		
		if 'quadrature_weights' in self.keys:
			self.quadrature_weights = self.file['quadrature_weights'][:]
		
		if 'dt' in self.keys:
			self.dt = self.file['dt'][()]
			self.times = np.arange(self.tmin, self.tmax+self.dt, self.dt)
			self.quadrature_weights = self.dt * np.ones(self.times.shape)
		
		if 'times' not in self.__dict__.keys():
			print "\n>>> Warning: No time samples found or generated."
		
		if 'quadrature_weights' not in self.__dict__.keys():
			print "\n>>> Warning: No quadrature weights found or generated."
		
		if 't_units' in self.keys:
			self.t_units = self.file['t_units'][()]
		else:
			self.t_units = 'TOverMtot'
		
		### Greedy points (ordered by RB selection) ###
		self.greedy_points = self.file['greedy_points'][:]
		
		### Empirical time index (ordered by EIM selection) ###
		self.eim_indices = self.file['eim_indices'][:]
		
		### Complex B coefficients ###
		self.B = self.file['B'][:]	
		
		### Information about phase/amp parametric fit ###
		self.affine_map = self.file['affine_map'][()]
		self.fitparams_amp = self.file['fitparams_amp'][:]
		self.fitparams_phase = self.file['fitparams_phase'][:]
		self.fit_min = self.file['fit_min'][()]
		self.fit_max = self.file['fit_max'][()]
		self.fit_interval = [self.fit_min, self.fit_max]
		
		self.fit_type_amp = self.chars_to_string(self.file['fit_type_amp'][()])
		self.fit_type_phase = self.chars_to_string(self.file['fit_type_phase'][()])
		
		self.amp_fit_func   = my_funcs[self.fit_type_amp]
		self.phase_fit_func = my_funcs[self.fit_type_phase]
		
		if 'fit_type_norm' in self.keys:
			self.fitparams_norm = self.file['fitparams_norm'][:]
			self.fit_type_norm = self.chars_to_string(self.file['fit_type_norm'][()])
			self.norm_fit_func  = my_funcs[self.fit_type_norm]
			self.norms = True
	
		else:
			self.norms = False
		
		if 'eim_amp' in self.keys:
			self.eim_amp = self.file['eim_amp'][:]
	
		if 'eim_phase' in self.keys:
			self.eim_phase = self.file['eim_phase'][:]
					
		### Transpose matrices if surrogate was built using ROMpy ###
		Bshape = np.shape(self.B)
	
		if Bshape[0] < Bshape[1]:
			transposeB = True
			self.B = np.transpose(self.B)
			self.dim_rb = Bshape[0]
			self.time_samples = Bshape[1]
	
		else:
			self.dim_rb = Bshape[1]
			self.time_samples = Bshape[0]
		
		### Vandermonde V such that E (orthogonal basis) is E = BV ###
		if 'V' in self.keys:
			self.V = self.file['V'][:]
			if transposeB:
				self.V = np.transpose(self.V)
	
		### R matrix such that waveform basis H = ER ###
		if 'R' in self.keys:
			self.R = self.file['R'][:]
			if transposeB:
				self.R = np.transpose(self.R)
		
		self.file.close()
		
		pass
		
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def write_h5(self, dict, path=None):
		""" Export surrogate data in standard format.
		
		Input:
		======
			dict -- Dictionary with surrogate data to export.
			
		NOTE: Run print_required() to print the list of 
		the minimum data required by GWSurrogate.
		"""
		
		if path is not None:
			file = h5py.File(path, 'w')
		else:
			file = self.file
		
		### Check that the minimum required surrogate data is given ###
		keys = self.check_required(dict)
		
		### Export surrogate data to HDF5 file ###
		for kk in keys:
		
			if kk != 'surrogate_ID':
		
				dtype = type(dict[kk])
				
				if dtype == str:
					chars = self.string_to_chars(dict[kk])
					file.create_dataset(kk, data=chars, dtype='int')
				
				elif dtype == np.ndarray:
					file.create_dataset(kk, data=dict[kk], dtype=dict[kk].dtype, compression='gzip')
				
				else:
					file.create_dataset(kk, data=dict[kk], dtype=type(dict[kk]))

			else:
				name = file.filename.split('/')[-1].split('.')[0]
				file.create_dataset('surrogate_ID', data=self.string_to_chars(name), dtype='int')
		
		### Close file ###		
		file.close()
		
		pass


##############################################
class ExportSurrogate(H5Surrogate, TextSurrogateWrite):
	"""Export single-mode surrogate"""
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def __init__(self, path):
		
		# export HDF5 or Text surrogate data depending on input file extension
		ext = path.split('.')[-1]
		if ext == 'hdf5' or ext == 'h5':
			H5Surrogate.__init__(self, file=path, mode='w')
		else:
			raise ValueError('use TextSurrogateWrite instead')


##############################################
class EvaluateSingleModeSurrogate(H5Surrogate, TextSurrogateRead):
	"""Evaluate single-mode surrogate in terms of the function's amplitude and phase"""
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def __init__(self, path, deg=3):
		
		# Load HDF5 or Text surrogate data depending on input file extension
		ext = path.split('.')[-1]
		if ext == 'hdf5' or ext == 'h5':
			H5Surrogate.__init__(self, file=path, mode='r')
		else:
			TextSurrogateRead.__init__(self, path)
		
		# Interpolate columns of the empirical interpolant operator, B, using cubic spline
		self.reB_spline_params = [splrep(self.times, self.B[:,jj].real, k=deg) for jj in range(self.dim_rb)]
		self.imB_spline_params = [splrep(self.times, self.B[:,jj].imag, k=deg) for jj in range(self.dim_rb)]
		
		# Convenience for plotting purposes
		self.plt = plt
		
		pass

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def __call__(self, q, M=None, dist=None, phi_ref=None, f_low=None, samples=None):
		"""Return surrogate evaluation for...
			q    = mass ratio (dimensionless) 
			M    = total mass (solar masses) 
			dist = distance to binary system (megaparsecs)
			phir = mode's phase at peak amplitude
			flow = instantaneous initial frequency, will check if flow_surrogate < flow """


		### evaluate rh/M surrogate. Physical surrogates are generated by applying additional operations. ###
		hp, hc = self.h_sur(q, samples=samples)


		### adjust phase if requested -- see routine for assumptions about mode's peak ###
		if (phi_ref is not None):
			h  = self.adjust_merger_phase(hp + 1.0j*hc,phi_ref)
			hp = h.real
			hc = h.imag


		### if (q,M,distance) requested, use scalings and norm fit to get a physical mode ###
		if( M is not None and dist is not None):
			amp0    = ((M * mks.Msun ) / (dist * mks.Mpcinm )) * ( mks.G / np.power(mks.c,2.0) )
			t_scale = mks.Msuninsec * M
		else:
			amp0    = 1.0
			t_scale = 1.0

		hp     = amp0 * hp
		hc     = amp0 * hc
		t      = self.time()
		t      = t_scale * t


		### check that surrogate's starting frequency is below f_low, otherwise throw a warning ###
		if f_low is not None:
			self.find_instant_freq(hp, hc, t, f_low)

		return t, hp, hc

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def affine_mapper_checker(self, q):
		"""map q to the standard interval [-1,1] if necessary. Also check is q within training interval"""

		qmin, qmax = self.fit_interval

		if( q < qmin or q > qmax):
			print "Warning: Surrogate not trained at requested parameter value" # needed to display in ipython notebook
			Warning("Surrogate not trained at requested parameter value")


		if self.affine_map:
			q_0 = 2.*(q - qmin)/(qmax - qmin) - 1.;
		else:
			q_0 = q

		return q_0


	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def norm_eval(self, q_0, affine_mapped=True):
		"""evaluate norm fit"""

		if( not(affine_mapped) ):
			q_0 = self.affine_mapper_checker(q_0)

		nrm_eval  = np.array([ self.norm_fit_func(self.fitparams_norm, q_0) ])
		return nrm_eval

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def h_sur(self, q, samples=None):
		"""evaluate surrogate at q. This returns dimensionless rh/M waveforms in units of t/M."""

		### Map q to the standard interval and check parameter validity ###
		q_0 = self.affine_mapper_checker(q)

		### Evaluate amp/phase/norm fits ###

		amp_eval   = np.array([ self.amp_fit_func(self.fitparams_amp[jj, 0:self.dim_rb], q_0) for jj in range(self.dim_rb) ])
		phase_eval = np.array([ self.phase_fit_func(self.fitparams_phase[jj, 0:self.dim_rb], q_0) for jj in range(self.dim_rb) ])
		if self.norms:
			nrm_eval = self.norm_eval(q_0)
		else:
			nrm_eval = 1.
		
		### Build dim_RB-vector fit evaluation of h ###
		h_EIM = amp_eval*np.exp(1j*phase_eval)
		
		### Surrogate modes hp and hc ###
		if samples == None:
			surrogate = np.dot(self.B, h_EIM)
		else:
			surrogate = np.dot(self.resample_B(samples), h_EIM)

		surrogate = nrm_eval * surrogate
		hp = surrogate.real
		#hp = hp.reshape([self.time_samples,])
		hc = surrogate.imag
		#hc = hc.reshape([self.time_samples,])

		return hp, hc
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def find_instant_freq(self, hp, hc, t, f_low = None):
		"""instantaneous frequency at t_start for 

                   h = A(t) exp(2 * pi * i * f(t) * t), 

                   where \partial_t A ~ \partial_t f ~ 0. If f_low passed will check its been achieved."""

		f_instant = gwtools.find_instant_freq(hp, hc, t)

		if f_low is None:
			return f_instant
		else:
			if f_instant > f_low:
				raise Warning, "starting frequency is "+str(f_instant)
			else:
				pass


	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def amp_phase(self,h):
        	"""Get amplitude and phase of waveform, h = A*exp(i*phi)"""
		return gwtools.amp_phase(h)


	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def phi_merger(self,h):
        	"""Phase of mode (typically 22) at amplitude's peak. h = A*exp(i*phi). Routine assumes peak is exactly on temporal grid, which it is for rh/M surrogates."""

		amp, phase = self.amp_phase(h)
		argmax_amp = np.argmax(amp)

		return phase[argmax_amp]


	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def adjust_merger_phase(self,h,phiref):
		"""Modify GW mode's phase such that at time of amplitude peak, t_peak, we have phase(t_peak) = phiref"""

		phimerger = self.phi_merger(h)
		phiadj    = phiref - phimerger

		return gwtools.modify_phase(h,phiadj)

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def timer(self,M_eval=None,dist_eval=None,phi_ref=None,f_low=None,samples=None):
		"""average time to evaluate surrogate waveforms. """

		qmin, qmax = self.fit_interval
		ran = np.random.uniform(qmin, qmax, 1000)

		tic = time.time()
		if M_eval is None:
			for i in ran:
				hp, hc = self.h_sur(i)
		else:
			for i in ran:
				t, hp, hc = self.__call__(i,M_eval,dist_eval,phi_ref,f_low,samples)

		toc = time.time()
		print 'Timing results (results quoted in seconds)...'
		print 'Total time to generate 1000 waveforms = ',toc-tic
		print 'Average time to generate a single waveform = ', (toc-tic)/1000.0
		pass
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# TODO: this routine might not serve a useful purpose -- think about it
	def time(self, units=None):
		# NOTE: Is Mtot the total mass of the surrogate or the total mass one wants to 
		# evaluate the time?
		"""Return time samples in specified units.
		
		Options for units:
		====================
		None		-- Time in geometric units, G=c=1 (DEFAULT)
		'solarmass' -- Time in units of solar masses
		'sec'		-- Time in units of seconds
		"""
		t = self.times
		if units == 'solarmass':
			t *= mks.Msuninsec
		elif units == 'sec':
			t *= mks.Msuninsec
		return t
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def basis(self, i, flavor='waveform'):
		"""compute the ith cardinal, orthogonal, or (exact, as opposed to 
                   its surrogate approximate) waveform basis."""

		if flavor == 'cardinal':
			basis = self.B[:,i]
		elif flavor == 'orthogonal':
			basis = np.dot(self.B,self.V)[:,i]
		elif flavor == 'waveform':
			E = np.dot(self.B,self.V)
			basis = np.dot(E,self.R)[:,i]
		else:
			raise ValueError("Not a valid basis type")

		return basis

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def resample_B(self, samples):
		"""resample the empirical interpolant operator, B, at the input samples"""
		return np.array([splev(samples, self.reB_spline_params[jj])  \
				+ 1j*splev(samples, self.imB_spline_params[jj]) for jj in range(self.dim_rb)]).T
		
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def plot_pretty(self, time, hp, hc, fignum=1, flavor='regular'):
		"""create a waveform figure with nice formatting and labels.
		returns figure method for saving, plotting, etc."""

		# Plot waveform
		fig = self.plt.figure(fignum)
		ax = fig.add_subplot(111)

		if flavor == 'regular':
			self.plt.plot(time, hp, 'k-', label='$h_+ (t)$')
			self.plt.plot(time, hc, 'k--', label='$h_\\times (t)$')
		elif flavor == 'semilogy':
			self.plt.semilogy(time, hp, 'k-', label='$h_+ (t)$')
			self.plt.semilogy(time, hc, 'k--', label='$h_\\times (t)$')
		else:
			raise ValueError("Not a valid plot type")

		self.plt.xlabel('Time, $t/M$')
		self.plt.ylabel('Waveform')
		self.plt.legend(loc='upper left')

		return fig
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def plot_rb(self, i, showQ=True):
		"""plot the ith reduced basis waveform"""
		
		# NOTE: Need to allow for different time units for plotting and labeling
		
		# Compute surrogate approximation of RB waveform
		basis = self.basis(i)
		hp    = basis.real
		hc    = basis.imag
		
		# Plot waveform
		fig = self.plot_pretty(self.times,hp,hc)
		
		if showQ:
			self.plt.show()
		
		# Return figure method to allow for saving plot with fig.savefig
		return fig
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def plot_sur(self, q_eval, timeM=False, showQ=True):
		"""plot surrogate evaluated at q_eval"""
		
		hp, hc = self.h_sur(q_eval)
		t      = self.time()

		if self.t_units == 'TOverMtot':
			#times = self.solarmass_over_mtot(times)
			xlab = 'Time, $t/M$'
		else:
			xlab = 'Time, $t$ (sec)'

		# Plot surrogate waveform
		fig = self.plot_pretty(t,hp,hc)
		self.plt.xlabel(xlab)
		self.plt.ylabel('Surrogate waveform')
		
		if showQ:
			self.plt.show()
		
		# Return figure method to allow for saving plot with fig.savefig
		return fig
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def writetxt(self, q_eval, filename='output'):
		"""write waveform to text file"""
		hp, hc = self(q_eval)
		np.savetxt(filename, [self.times, hp, hc])
		pass

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def writebin(self, q_eval, filename='output.txt'): # .txt for binary?
		"""write waveform to numpy binary file"""
		hp, hc = self(q_eval)
		np.save(filename, [self.times, hp, hc])
		pass


##############################################
class EvaluateSurrogate(EvaluateSingleModeSurrogate): 
# TODO: inherated from EvalSingleModeSurrogate to gain access to some functions. this should be better structured
	"""Evaluate multi-mode surrogates"""
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def __init__(self, path, deg=3):


		# Convenience for plotting purposes
		self.plt = plt

		### fill up dictionary of single mode surrogate class ###
		self.single_modes = dict()

		# Load HDF5 or Text surrogate data depending on input file extension
		ext = path.split('.')[-1]
		if ext == 'hdf5' or ext == 'h5':
			raise ValueError('Not coded yet')
		else:
			### compile list of available modes ###
			# assumes (i) single mode folder format l#_m#_ (ii) ell<=9, m>=0
			for single_mode in list_folders(path,'l'):
				mode_key = single_mode[0:5]
				print "loading surrogate mode... "+mode_key
				self.single_modes[mode_key] = EvaluateSingleModeSurrogate(path+single_mode+'/')

	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	def __call__(self, q, M=None, dist=None, phi_ref=None, f_low=None, samples=None, ell=None, m=None):
		"""Return surrogate evaluation for...
			q    = mass ratio (dimensionless) 
			M    = total mass (solar masses) 
			dist = distance to binary system (megaparsecs)
			phir = mode's phase at peak amplitude
			flow = instantaneous initial frequency, will check if flow_surrogate < flow 
			ell = list or array of N ell modes to evaluate for (if none, all modes are returned)
			m   = for each ell, supply a matching m value 

                    NOTE: if only requesting one mode, this should be ell=[2],m=[2]"""

		if ell is None:
			raise ValueError('code me')
		else:
			if len(ell) > 1:
				raise ValueError('sum over modes not coded yet')
			modes = [(x, y) for x in ell for y in m]
			for ell,m in modes:
				if m >= 0:
					mode_key = 'l'+str(ell)+'_m'+str(m)
					t_mode, hp_mode, hc_mode = self.single_modes[mode_key](q, M, dist, phi_ref, f_low, samples)
				else: # h(l,-m) = (-1)^l h(l,m)^*
					# TODO: CHECK THESE EXPRESSIONS AGAINST SPEC OR LAL OUTPUT
					mode_key = 'l'+str(ell)+'_m'+str(int(-m))
					t_mode, hp_mode, hc_mode = self.single_modes[mode_key](q, M, dist, phi_ref, f_low, samples)
					hp_mode =   np.power(-1,ell) * hp_mode
					hc_mode = - np.power(-1,ell) * hc_mode

		return t_mode, hp_mode, hc_mode


####################################################
def CompareSingleModeSurrogate(sur1,sur2):
  """ Compare data defining two surrogates"""

  #TODO: should loop over necessary and optional data fields in future SurrogateIO class

  for key in sur1.__dict__.keys():

    if key in ['B','V','R','fitparams_phase','fitparams_amp',\
               'fitparams_norm','greedy_points','eim_indices']:

      if np.max(np.abs(sur1.__dict__[key] - sur2.__dict__[key])) != 0:
        print "checking attribute "+str(key)+"...DIFFERENT!!!"
      else:
        print "checking attribute "+str(key)+"...agrees"

    elif key in ['fit_type_phase','fit_type_amp','fit_type_norm']:

      if sur1.__dict__[key] == sur2.__dict__[key]:
        print "checking attribute "+str(key)+"...agrees"
      else:
         print "checking attribute "+str(key)+"...DIFFERENT!!!"

    else:
      print "not checking attribute "+str(key)



