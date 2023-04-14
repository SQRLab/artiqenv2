from artiq.coredevice.ad9910 import RAM_MODE_CONT_RAMPUP
import artiq.coredevice.ad9910
from artiq.experiment import *
from dax.experiment import *
from numpy import int32, int64
from artiq.coredevice.urukul import DEFAULT_PROFILE

__all__ = ['DdsModule']

_PHASE_MODE_DEFAULT = -1
PHASE_MODE_CONTINUOUS = 0
PHASE_MODE_ABSOLUTE = 1
PHASE_MODE_TRACKING = 2

_AD9910_REG_CFR1 = 0x00
_AD9910_REG_CFR2 = 0x01
_AD9910_REG_CFR3 = 0x02
_AD9910_REG_AUX_DAC = 0x03
_AD9910_REG_IO_UPDATE = 0x04
_AD9910_REG_FTW = 0x07
_AD9910_REG_POW = 0x08
_AD9910_REG_ASF = 0x09
_AD9910_REG_SYNC = 0x0a
_AD9910_REG_RAMP_LIMIT = 0x0b
_AD9910_REG_RAMP_STEP = 0x0c
_AD9910_REG_RAMP_RATE = 0x0d
_AD9910_REG_PROFILE0 = 0x0e
_AD9910_REG_PROFILE1 = 0x0f
_AD9910_REG_PROFILE2 = 0x10
_AD9910_REG_PROFILE3 = 0x11
_AD9910_REG_PROFILE4 = 0x12
_AD9910_REG_PROFILE5 = 0x13
_AD9910_REG_PROFILE6 = 0x14
_AD9910_REG_PROFILE7 = 0x15
_AD9910_REG_RAM = 0x16

# RAM destination
RAM_DEST_FTW = 0
RAM_DEST_POW = 1
RAM_DEST_ASF = 2
RAM_DEST_POWASF = 3

# RAM MODES
RAM_MODE_DIRECTSWITCH = 0
RAM_MODE_RAMPUP = 1
RAM_MODE_BIDIR_RAMP = 2
RAM_MODE_CONT_BIDIR_RAMP = 3
RAM_MODE_CONT_RAMPUP = 4

# Default profile for RAM mode
_DEFAULT_PROFILE_RAM = 0
class DdsModule(DaxModule):
	#Module to set up all the dds outputs cplds are handled by Dax separately
	
	_init_kernel: bool
	
	def build(self, *urukuls: str, init_kernel: bool = False) -> None:  # type: ignore[override]
		"""Build the dds Output module.
		:param urukuls: Keys of the dds urukul output devices to use in order from least to most significant
		:param init_kernel: Run initialization kernel during default module initialization
		"""
		
		# Check arguments, there are 3chips x4channels urukul outputs
		if not 1<= len(urukuls) <= 12:
			raise TypeError("Number of Urukul's must be in the range urukul{0,1,2}ch{0,1,2,3} with 12 maximum urukul output channels")
		#else:
		#	#print("urukuls",urukuls)
		assert all(isinstance(urukul, str) for urukul in urukuls), 'Provided urukul keys must be of type str'
		assert isinstance(init_kernel, bool), 'Init kernel flag must be of type bool'

		# store attributes
		self._init_kernel = init_kernel
		self.logger.debug(f'Init kernel: {self._init_kernel}')
		
		#urukul array
		self.dds = [self.get_device(urukul, artiq.coredevice.ad9910.AD9910) for urukul in urukuls]
		self.update_kernel_invariants('dds')
		self.logger.debug(f"Number of DDS Output's: {len(self.dds)}")
		
	def init(self, *, force: bool = False) -> None:
		"""Initialize module
	
		:param force: Force full initalization
		"""
		if self._init_kernel or force:
			# Initialize the urukuls if the init flag is set
			self.logger.debug('Running initialization kernel for dds')
			self.init_kernel()
		
	@kernel
	def init_kernel(self):  # type: () -> None
		"""Kernel function to initialize this module.
		This function is called automatically during initialization unless the user configured otherwise.
		In that case, this function has to be called manually.
		"""
		# Reset the core
		self.core.reset()

		# Turn all dds's off?
		#self.off_all()

		# Wait until event is submitted
		self.core.wait_until_mu(now_mu())

	def post_init(self) -> None:
		pass

	"""Module functionality from artiq.ad9910 but adapted to local format"""
	
	@kernel
	def set_phase_mode(self, phase_mode: TInt32,index: TInt32 = 0):
		""" Phase modes are:
		_PHASE_MODE_DEFAULT = -1 to set whichever one the system considers default right now should be continuous (0)
		PHASE_MODE_CONTINUOUS = 0 to set output phase to remain continuous unless phase offset is changed
		PHASE_MODE_ABSOLUTE = 1 to set output phase to be the phase offset when either phase offset or frequency is changed
		PHASE_MODE_TRACKING = 2 to set output phase to be what it would have been running under the new settings from when it started this is the 'coherent phase mode'
		"""
		self.dds[index].set_phase_mode(phase_mode)




	@kernel
	def write16(self, addr: TInt32, data: TInt32, index: TInt32 = 0):
		"""Write to 16 bit register.
		:param addr: Register address
		:param data: Data to be written
		"""
		self.dds[index].write16(addr,data)

	@kernel
	def write32(self, addr: TInt32, data: TInt32, index: TInt32 = 0):
		"""Write to 32 bit register.
		:param addr: Register address
		:param data: Data to be written
		"""
		self.dds[index].write32(addr,data)

	@kernel
	def read16(self, addr: TInt32, index: TInt32 = 0) -> TInt32:
		"""Read from 16 bit register.
		:param addr: Register address
		"""
		return self.dds[index].read16(addr)

	@kernel
	def read32(self, addr: TInt32, index: TInt32 = 0) -> TInt32:
		"""Read from 32 bit register.
		:param addr: Register address
		"""
		return self.dds[index].read32(addr)

	@kernel
	def read64(self, addr: TInt32, index: TInt32 = 0) -> TInt64:
		"""Read from 64 bit register.
		:param addr: Register address
		:return: 64 bit integer register value
		"""
		return self.dds[index].read64(addr)

	@kernel
	def write64(self, addr: TInt32, data_high: TInt32, data_low: TInt32, index: TInt32 = 0):
		"""Write to 64 bit register.
		:param addr: Register address
		:param data_high: High (MSB) 32 bits of the data
		:param data_low: Low (LSB) 32 data bits
		"""
		self.dds[index].write64(addr, data_high, data_low)

	@kernel
	def write_ram(self, data: TList(TInt32),index: TInt32 = 0):
		"""Write data to RAM.
		The profile to write to and the step, start, and end address
		need to be configured before and separately using
		:meth:`set_profile_ram` and the parent CPLD `set_profile`.
		:param data: Data to be written to RAM.
		"""
		self.dds[index].write_ram(data)
		
	@kernel
	def read_ram(self, data: TList(TInt32),index: TInt32 = 0):
		"""Read data from RAM.
		The profile to read from and the step, start, and end address
		need to be configured before and separately using
		:meth:`set_profile_ram` and the parent CPLD `set_profile`.
		:param data: List to be filled with data read from RAM.
		"""
		self.dds[index].read_ram(data)

	@kernel
	def set_cfr1(self,
		power_down: TInt32 = 0b0000,
		phase_autoclear: TInt32 = 0,
		drg_load_lrr: TInt32 = 0,
		drg_autoclear: TInt32 = 0,
		phase_clear: TInt32 = 0,
		internal_profile: TInt32 = 0,
		ram_destination: TInt32 = 0,
		ram_enable: TInt32 = 0,
		manual_osk_external: TInt32 = 0,
		osk_enable: TInt32 = 0,
		select_auto_osk: TInt32 = 0, index: TInt32 = 0):
		"""Set CFR1. See the AD9910 datasheet for parameter meanings.
		This method does not pulse IO_UPDATE.
		:param power_down: Power down bits.
		:param phase_autoclear: Autoclear phase accumulator.
		:param phase_clear: Asynchronous, static reset of the phase accumulator.
		:param drg_load_lrr: Load digital ramp generator LRR.
		:param drg_autoclear: Autoclear digital ramp generator.
		:param internal_profile: Internal profile control.
		:param ram_destination: RAM destination
			(:const:`RAM_DEST_FTW`, :const:`RAM_DEST_POW`,
			:const:`RAM_DEST_ASF`, :const:`RAM_DEST_POWASF`).
		:param ram_enable: RAM mode enable.
		:param manual_osk_external: Enable OSK pin control in manual OSK mode.
		:param osk_enable: Enable OSK mode.
		:param select_auto_osk: Select manual or automatic OSK mode.
		"""
		self.dds[index].set_cfr1(power_down,phase_autoclear,drg_load_lrr,
			drg_autoclear,phase_clear,internal_profile,ram_destination,
			ram_enable,manual_osk_external,osk_enable,select_auto_osk)

	@kernel
	def set_cfr2(self, 
		asf_profile_enable: TInt32 = 1, 
		drg_enable: TInt32 = 0, 
		effective_ftw: TInt32 = 1,
		sync_validation_disable: TInt32 = 0, 
		matched_latency_enable: TInt32 = 0, index: TInt32 = 0):
		"""Set CFR2. See the AD9910 datasheet for parameter meanings.
		This method does not pulse IO_UPDATE.
		:param asf_profile_enable: Enable amplitude scale from single tone profiles.
		:param drg_enable: Digital ramp enable.
		:param effective_ftw: Read effective FTW.
		:param sync_validation_disable: Disable the SYNC_SMP_ERR pin indicating
			(active high) detection of a synchronization pulse sampling error.
		:param matched_latency_enable: Simultaneous application of amplitude,
			phase, and frequency changes to the DDS arrive at the output
			* matched_latency_enable = 0: in the order listed
			* matched_latency_enable = 1: simultaneously.
		"""
		self.dds[index].set_cfr2(asf_profile_enable,drg_enable,effective_ftw,
			sync_validation_disable,matched_latency_enable)

# I think since this is a kernel init, the double name-bind is a non-issue, but that's worth checking
	@kernel
	def init(self, blind: TBool = False, index: TInt32 = 0):
		"""Initialize and configure the DDS.
		Sets up SPI mode, confirms chip presence, powers down unused blocks,
		configures the PLL, waits for PLL lock. Uses the
		IO_UPDATE signal multiple times.
		:param blind: Do not read back DDS identity and do not wait for lock.
		"""
		self.dds[index].init(blind)


	@kernel
	def power_down(self, bits: TInt32 = 0b1111, index: TInt32 = 0):
		"""Power down DDS.
		:param bits: Power down bits, see datasheet
		"""
		self.dds[index].power_down(bits)

	@kernel
	def set_mu(self, ftw: TInt32 = 0, pow_: TInt32 = 0, asf: TInt32 = 0x3fff,
		phase_mode: TInt32 = _PHASE_MODE_DEFAULT,
		ref_time_mu: TInt64 = int64(-1),
		profile: TInt32 = DEFAULT_PROFILE,
		ram_destination: TInt32 = -1, index: TInt32 = 0) -> TInt32:
		"""Set DDS data in machine units.
		This uses machine units (FTW, POW, ASF). The frequency tuning word
		width is 32, the phase offset word width is 16, and the amplitude
		scale factor width is 14.
		After the SPI transfer, the shared IO update pin is pulsed to
		activate the data.
		.. seealso: :meth:`set_phase_mode` for a definition of the different
		phase modes.
		:param ftw: Frequency tuning word: 32 bit.
		:param pow_: Phase tuning word: 16 bit unsigned.
		:param asf: Amplitude scale factor: 14 bit unsigned.
		:param phase_mode: If specified, overrides the default phase mode set
		by :meth:`set_phase_mode` for this call.
		:param ref_time_mu: Fiducial time used to compute absolute or tracking
		phase updates. In machine units as obtained by `now_mu()`.
		:param profile: Single tone profile number to set (0-7, default: 7).
		Ineffective if `ram_destination` is specified.
		:param ram_destination: RAM destination (:const:`RAM_DEST_FTW`,
		:const:`RAM_DEST_POW`, :const:`RAM_DEST_ASF`,
		:const:`RAM_DEST_POWASF`). If specified, write free DDS parameters
		to the ASF/FTW/POW registers instead of to the single tone profile
		register (default behaviour, see `profile`).
		:return: Resulting phase offset word after application of phase
		tracking offset. When using :const:`PHASE_MODE_CONTINUOUS` in
		subsequent calls, use this value as the "current" phase.
		"""

		return self.dds[index].set_mu(ftw,pow,asf,phase_mode,
			ref_time_mu,profile,ram_destination)

	@kernel
	def get_mu(self, profile: TInt32 = DEFAULT_PROFILE, index: TInt32 = 0
		) -> TTuple([TInt32, TInt32, TInt32]):
		"""Get the frequency tuning word, phase offset word,
		and amplitude scale factor.
		.. seealso:: :meth:`get`
		:param profile: Profile number to get (0-7, default: 7)
		:return: A tuple ``(ftw, pow, asf)``
		"""
		return self.dds[index].get_mu(profile)
		
	@kernel
	def set_profile_ram(self, start: TInt32, end: TInt32, step: TInt32 = 1,
		profile: TInt32 = _DEFAULT_PROFILE_RAM,
		nodwell_high: TInt32 = 0, zero_crossing: TInt32 = 0,
		mode: TInt32 = 1, index: TInt32 = 0):
		"""Set the RAM profile settings.
		:param start: Profile start address in RAM.
		:param end: Profile end address in RAM (last address).
		:param step: Profile time step in units of t_DDS, typically 4 ns
			(default: 1).
		:param profile: Profile index (0 to 7) (default: 0).
		:param nodwell_high: No-dwell high bit (default: 0,
			see AD9910 documentation).
		:param zero_crossing: Zero crossing bit (default: 0,
			see AD9910 documentation).
		:param mode: Profile RAM mode (:const:`RAM_MODE_DIRECTSWITCH`,
			:const:`RAM_MODE_RAMPUP`, :const:`RAM_MODE_BIDIR_RAMP`,
			:const:`RAM_MODE_CONT_BIDIR_RAMP`, or
			:const:`RAM_MODE_CONT_RAMPUP`, default:
		:const:`RAM_MODE_RAMPUP`)
		"""
		self.dds[index].set_profile_ram(start,end,step,profile,
			nodwell_high,zero_crossing,mode)

	@kernel
	def set_ftw(self, ftw: TInt32, index: TInt32 = 0):
		"""Set the value stored to the AD9910's frequency tuning word (FTW)
		register.
		:param ftw: Frequency tuning word to be stored, range: 0 to 0xffffffff.
		"""
		self.dds[index].set_ftw(ftw)

	@kernel
	def set_asf(self, asf: TInt32, index: TInt32 = 0):
		"""Set the value stored to the AD9910's amplitude scale factor (ASF)
		register.
		:param asf: Amplitude scale factor to be stored, range: 0 to 0x3fff.
		"""
		self.dds[index].set_asf(asf)

	@kernel
	def set_pow(self, pow_: TInt32, index: TInt32 = 0):
		"""Set the value stored to the AD9910's phase offset word (POW)
		register.
		:param pow_: Phase offset word to be stored, range: 0 to 0xffff.
		"""
		self.dds[index].set_pow(pow)

	@kernel
	def get_ftw(self, index: TInt32 = 0) -> TInt32:
		"""Get the value stored to the AD9910's frequency tuning word (FTW)
		register.
		:return: Frequency tuning word
		"""
		return self.dds[index].get_ftw()

	@kernel
	def get_asf(self, index: TInt32 = 0) -> TInt32:
		"""Get the value stored to the AD9910's amplitude scale factor (ASF)
		register.
		:return: Amplitude scale factor
		"""
		return self.dds[index].get_asf()

	@kernel
	def get_pow(self, index: TInt32 = 0) -> TInt32:
		"""Get the value stored to the AD9910's phase offset word (POW)
		register.
		:return: Phase offset word
		"""
		return self.dds[index].get_pow()

	@portable(flags={"fast-math"})
	def frequency_to_ftw(self, frequency: TFloat, index: TInt32 = 0) -> TInt32:
		"""Return the 32-bit frequency tuning word corresponding to the given
		frequency.
		"""
		return self.dds[index].frequency_to_ftw(frequency)

	@portable(flags={"fast-math"})
	def ftw_to_frequency(self, ftw: TInt32, index: TInt32 = 0) -> TFloat:
		"""Return the frequency corresponding to the given frequency tuning
		word.
		"""
		return self.dds[index].ftw_to_frequency(ftw)

	@portable(flags={"fast-math"})
	def turns_to_pow(self, turns: TFloat, index: TInt32 = 0) -> TInt32:
		"""Return the 16-bit phase offset word corresponding to the given phase
		in turns."""
		return self.dds[index].turns_to_pow(turns)

	@portable(flags={"fast-math"})
	def pow_to_turns(self, pow_: TInt32, index: TInt32 = 0) -> TFloat:
		"""Return the phase in turns corresponding to a given phase offset
		word."""
		return self.dds[index].pow_to_turns(pow_)

	@portable(flags={"fast-math"})
	def amplitude_to_asf(self, amplitude: TFloat, index: TInt32 = 0) -> TInt32:
		"""Return 14-bit amplitude scale factor corresponding to given
		fractional amplitude."""
		return self.dds[index].amplitude_to_asf(amplitude)
		
	@portable(flags={"fast-math"})
	def asf_to_amplitude(self, asf: TInt32, index: TInt32 = 0) -> TFloat:
		"""Return amplitude as a fraction of full scale corresponding to given
		amplitude scale factor."""
		return self.dds[index].asf_to_amplitude(asf)

	@portable(flags={"fast-math"})
	def frequency_to_ram(self, frequency: TList(TFloat), ram: TList(TInt32),
		 index: TInt32 = 0):
		"""Convert frequency values to RAM profile data.
		To be used with :const:`RAM_DEST_FTW`.
		:param frequency: List of frequency values in Hz.
		:param ram: List to write RAM data into.
			Suitable for :meth:`write_ram`.
		"""
		self.dds[index].frequency_to_ram(frequency, ram)

	@portable(flags={"fast-math"})
	def turns_to_ram(self, turns: TList(TFloat), ram: TList(TInt32), index: TInt32 = 0):
		"""Convert phase values to RAM profile data.
		To be used with :const:`RAM_DEST_POW`.
		:param turns: List of phase values in turns.
		:param ram: List to write RAM data into.
			Suitable for :meth:`write_ram`.
		"""
		self.dds[index].turns_to_ram(turns, ram)

	@portable(flags={"fast-math"})
	def amplitude_to_ram(self, amplitude: TList(TFloat), ram: TList(TInt32),
		 index: TInt32 = 0):
		"""Convert amplitude values to RAM profile data.
		To be used with :const:`RAM_DEST_ASF`.
		:param amplitude: List of amplitude values in units of full scale.
		:param ram: List to write RAM data into.
			Suitable for :meth:`write_ram`.
		"""
		self.dds[index].amplitude_to_ram(amplitude, ram)

	@portable(flags={"fast-math"})
	def turns_amplitude_to_ram(self, turns: TList(TFloat),
		amplitude: TList(TFloat), ram: TList(TInt32), index: TInt32 = 0):
		"""Convert phase and amplitude values to RAM profile data.
		To be used with :const:`RAM_DEST_POWASF`.
		:param turns: List of phase values in turns.
		:param amplitude: List of amplitude values in units of full scale.
		:param ram: List to write RAM data into.
			Suitable for :meth:`write_ram`.
		"""
		self.dds[index].turns_amplitude_to_ram(turns,amplitude, ram)

	@kernel
	def set_frequency(self, frequency: TFloat, index: TInt32 = 0):
		"""Set the value stored to the AD9910's frequency tuning word (FTW)
		register.
		:param frequency: frequency to be stored, in Hz.
		"""
		self.dds[index].set_frequency(frequency)

	@kernel
	def set_amplitude(self, amplitude: TFloat, index: TInt32 = 0):
		"""Set the value stored to the AD9910's amplitude scale factor (ASF)
		register.
		:param amplitude: amplitude to be stored, in units of full scale.
		"""
		self.dds[index].set_amplitude(amplitude)

	@kernel
	def set_phase(self, turns: TFloat, index: TInt32 = 0):
		"""Set the value stored to the AD9910's phase offset word (POW)
		register.
		:param turns: phase offset to be stored, in turns.
		"""
		self.dds[index].set_phase(turns)

	@kernel
	def get_frequency(self, index: TInt32 = 0) -> TFloat:
		"""Get the value stored to the AD9910's frequency tuning word (FTW)
		register.
		:return: frequency in Hz.
		"""
		return self.dds[index].get_frequency()

	@kernel
	def get_amplitude(self, index: TInt32 = 0) -> TFloat:
		"""Get the value stored to the AD9910's amplitude scale factor (ASF)
		register.
		:return: amplitude in units of full scale.
		"""
		return self.dds[index].get_amplitude()

	@kernel
	def get_phase(self, index: TInt32 = 0) -> TFloat:
		"""Get the value stored to the AD9910's phase offset word (POW)
		register.
		:return: phase offset in turns.
		"""
		return self.dds[index].get_phase()

	@kernel
	def set(self, frequency: TFloat = 0.0, phase: TFloat = 0.0,
		amplitude: TFloat = 1.0, phase_mode: TInt32 = _PHASE_MODE_DEFAULT,
		ref_time_mu: TInt64 = int64(-1), profile: TInt32 = DEFAULT_PROFILE,
		ram_destination: TInt32 = -1, index: TInt32 = 0) -> TFloat:
		"""Set DDS data in SI units.
		.. seealso:: :meth:`set_mu`
		:param frequency: Frequency in Hz
		:param phase: Phase tuning word in turns
		:param amplitude: Amplitude in units of full scale
		:param phase_mode: Phase mode constant
		:param ref_time_mu: Fiducial time stamp in machine units
		:param profile: Single tone profile to affect.
		:param ram_destination: RAM destination.
		:return: Resulting phase offset in turns
		"""
		return self.dds[index].set(frequency, phase, amplitude,
			 phase_mode, ref_time_mu, profile, ram_destination)

	@kernel
	def get(self, profile: TInt32 = DEFAULT_PROFILE, index: TInt32 = 0
		) -> TTuple([TFloat, TFloat, TFloat]):
		"""Get the frequency, phase, and amplitude.
		.. seealso:: :meth:`get_mu`
		:param profile: Profile number to get (0-7, default: 7)
		:return: A tuple ``(frequency, phase, amplitude)``
		"""
		return self.dds[index].get(profile)

	@kernel
	def set_att_mu(self, att: TInt32, index: TInt32 = 0):
		"""Set digital step attenuator in machine units.
		This method will write the attenuator settings of all four channels.
		.. seealso:: :meth:`artiq.coredevice.urukul.CPLD.set_att_mu`
		:param att: Attenuation setting, 8 bit digital.
		"""
		self.dds[index].set_att_mu(att)

	@kernel
	def set_att(self, att: TFloat, index: TInt32 = 0):
		"""Set digital step attenuator in SI units.
		This method will write the attenuator settings of all four channels.
		.. seealso:: :meth:`artiq.coredevice.urukul.CPLD.set_att`
		:param att: Attenuation in dB.
		"""
		self.dds[index].set_att(att)

	@kernel
	def get_att_mu(self, index: TInt32 = 0) -> TInt32:
		"""Get digital step attenuator value in machine units.
		.. seealso:: :meth:`artiq.coredevice.urukul.CPLD.get_channel_att_mu`
		:return: Attenuation setting, 8 bit digital.
		"""
		return self.dds[index].get_att_mu()

	@kernel
	def get_att(self, index: TInt32 = 0) -> TFloat:
		"""Get digital step attenuator value in SI units.
		.. seealso:: :meth:`artiq.coredevice.urukul.CPLD.get_channel_att`
		:return: Attenuation in dB.
		"""
		return self.dds[index].get_att()

	@kernel
	def cfg_sw(self, state: TBool, index: TInt32 = 0):
		"""Set CPLD CFG RF switch state. The RF switch is controlled by the
		logical or of the CPLD configuration shift register
		RF switch bit and the SW TTL line (if used).
		:param state: CPLD CFG RF switch bit
		"""
		self.dds[index].cfg_sw(state)

####Largely Unedited as of yet below here

	@kernel
	def set_sync(self, 
		in_delay: TInt32, 
		window: TInt32, 
		en_sync_gen: TInt32 = 0, index: TInt32 = 0):
		"""Set the relevant parameters in the multi device synchronization
		register. See the AD9910 datasheet for details. The SYNC clock
		generator preset value is set to zero, and the SYNC_OUT generator is
		disabled by default.
		:param in_delay: SYNC_IN delay tap (0-31) in steps of ~75ps
		:param window: Symmetric SYNC_IN validation window (0-15) in
			steps of ~75ps for both hold and setup margin.
		:param en_sync_gen: Whether to enable the DDS-internal sync generator
			(SYNC_OUT, cf. sync_sel == 1). Should be left off for the normal
			use case, where the SYNC clock is supplied by the core device.
		"""
		self.dds[index].set_sync(in_delay, window, en_sync_gen)
	@kernel
	def clear_smp_err(self, index: TInt32 = 0):
		"""Clear the SMP_ERR flag and enables SMP_ERR validity monitoring.
		Violations of the SYNC_IN sample and hold margins will result in
		SMP_ERR being asserted. This then also activates the red LED on
		the respective Urukul channel.
		Also modifies CFR2.
		"""
		self.dds[index].clear_smp_err()

	@kernel
	def tune_sync_delay(self,
		search_seed: TInt32 = 15, index: TInt32 = 0) -> TTuple([TInt32, TInt32]):
		"""Find a stable SYNC_IN delay.
		This method first locates a valid SYNC_IN delay at zero validation
		window size (setup/hold margin) by scanning around `search_seed`. It
		then looks for similar valid delays at successively larger validation
		window sizes until none can be found. It then decreases the validation
		window a bit to provide some slack and stability and returns the
		optimal values.
		This method and :meth:`tune_io_update_delay` can be run in any order.
		:param search_seed: Start value for valid SYNC_IN delay search.
			Defaults to 15 (half range).
		:return: Tuple of optimal delay and window size.
		"""
		self.dds[index].tune_sync_delay(search_seed)

	@kernel
	def measure_io_update_alignment(self, delay_start: TInt64,
		delay_stop: TInt64, index: TInt32 = 0) -> TInt32:
		"""Use the digital ramp generator to locate the alignment between
		IO_UPDATE and SYNC_CLK.
		The ramp generator is set up to a linear frequency ramp
		(dFTW/t_SYNC_CLK=1) and started at a coarse RTIO time stamp plus
		`delay_start` and stopped at a coarse RTIO time stamp plus
		`delay_stop`.
		:param delay_start: Start IO_UPDATE delay in machine units.
		:param delay_stop: Stop IO_UPDATE delay in machine units.
		:return: Odd/even SYNC_CLK cycle indicator.
		"""
		return self.dds[index].measure_io_update_alignment(delay_start,delay_stop)

	@kernel
	def tune_io_update_delay(self, index: TInt32 = 0) -> TInt32:
		"""Find a stable IO_UPDATE delay alignment.
		Scan through increasing IO_UPDATE delays until a delay is found that
		lets IO_UPDATE be registered in the next SYNC_CLK cycle. Return a
		IO_UPDATE delay that is as far away from that SYNC_CLK edge
		as possible.
		This method assumes that the IO_UPDATE TTLOut device has one machine
		unit resolution (SERDES).
		This method and :meth:`tune_sync_delay` can be run in any order.
		:return: Stable IO_UPDATE delay to be passed to the constructor
		:class:`AD9910` via the device database.
		"""
		return self.dds[index].tune_io_update_delay()
		
		
