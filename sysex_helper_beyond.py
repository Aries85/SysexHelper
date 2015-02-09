import array
import beyond.Reaper
import tkinter

from tkinter import *


# TODO - add loading support
sysex = [
		("Drum Track On", bytes.fromhex("42 30 00 01 05 41 00 00 0B 00 0A 00 00 00 00 01")),
		("Drum Track Off", bytes.fromhex("42 30 00 01 05 41 00 00 0B 00 0A 00 00 00 00 00"))
	]

button_states = []
		
class my_app(Frame):
	"""Basic Frame"""
	last_pos = 0
	buttons = []
	
	def __init__(self, master):
		"""Init the Frame"""
		Frame.__init__(self,master)
		self.grid()
		for index in range(0, len(sysex)):
			button_states.append(tkinter.IntVar())
			button_state_variable = button_states[index]
			button = Checkbutton(self, text = sysex[index][0], anchor = W, onvalue=1, offvalue=0, variable=button_state_variable , command =  lambda index=index: self.access(index))
			button.config(height = 3, width = 30)
			button.grid(column = 0, row = index, sticky = NW)
			self.buttons.append(button)
			self.last_pos = Reaper.RPR_GetCursorPosition()
		self.update_controls()
			
	def update_controls(self):
		selectedTrack = Reaper.RPR_GetSelectedTrack(0, 0);
		
		# TODO add caching
		cursor_pos = Reaper.RPR_GetCursorPosition()
		
		for i in range(0, Reaper.RPR_CountTrackMediaItems(selectedTrack)):
			item_id = Reaper.RPR_GetTrackMediaItem(selectedTrack, i)
			take = Reaper.RPR_GetActiveTake(item_id);
			pos = Reaper.RPR_GetMediaItemInfo_Value(item_id, "D_POSITION");
			length = Reaper.RPR_GetMediaItemInfo_Value(item_id, "D_LENGTH");
			end_pos = pos + length
			current_pos_ppq = Reaper.RPR_MIDI_GetPPQPosFromProjTime(take, cursor_pos);
			if (cursor_pos >= pos + 0.001) and (cursor_pos <= end_pos + 0.001):
				
				# current_pos_ppq = Reaper.RPR_MIDI_GetPPQPosFromProjTime(take, cursor_pos);
				# iterate over Sysex events, get status
				num_sysex = Reaper.RPR_MIDI_CountEvts(take, 0, 0, 0)[0]
				print("Num sysex: " + str(num_sysex))
				for j in range(0, num_sysex):
					# ta_ prefix for throw away
					(ta_retval, ta_take, ta_textsyxevtidx, ta_selectedOutOptional, ta_mutedOutOptional, current_evt_pos_ppq, current_evt_type, current_msg, msgOptional_sz) = Reaper.RPR_MIDI_GetTextSysexEvt(take, j, 0, 0, 0, 0, 0, 0)
					current_msg = Reaper.RPR_MIDI_GetTextSysexEvt(take, j, 0, 0, 0, 0, 0, 0)[7]
					if current_evt_type == -1:
						print("Sysex event number " + str(j))
						# yes, this is a sysex message
						if current_pos_ppq == current_evt_pos_ppq:
							print("Sysex event is on cursor position")
							print("Sysex event data: %s" % ''.join('{:02X}'.format(int(a)) for a in current_msg))
							# yes, it is on current cursor position
							# iterate over defined sysexes
							print("Configuration iteration")
							for conf_id in range(0, len(sysex)):
								print("Current configuration data: %s" % ''.join('{:02X}'.format(int(a)) for a in sysex[conf_id][1]))
								# print("Current configuration data: %s" % sysex[conf_id][1])
								if current_msg == sysex[conf_id][1]:
									print("Found sysex event for button switching")
									self.buttons[conf_id].config(relief = "sunken")
									break
	
	def access(self, b_id):
		self.b_id = b_id
		clicked_button = self.buttons[b_id]
		# get state, it is state after clicking
		checked = button_states[b_id].get()
		if checked:
			# add event on cursor position
			print("Would add sysex event on cursor position")
		else:
			# remove event under cursor
			print("Would remove sysex event under cursor")
			
		
@ProgramStartDirect
def Main():
	root = Tk()
	root.title("SysEx helper")
	root.geometry("500x500")
	app = my_app(root)
	root.mainloop()