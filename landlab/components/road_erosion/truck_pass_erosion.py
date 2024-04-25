"""
Purpose: Practice Landlab component building - Road Erosion Component
Author: Amanda Manaster
Date: 06/08/2018
"""
#testing 1,2,3...


from landlab import Component
from landlab.components import LinearDiffuser
import random as rnd
import numpy as np

class TruckPassErosion(Component):
    
    _name = 'TruckPassErosion'
    
    _input_var_names = (
        'topographic__elevation',
        'soil__depth',
    )
    
    _output_var_names = (        
        'topographic__elevation',
        'soil__depth',
    )
    
    _var_units = {
        'topographic__elevation': 'm',
        'soil__depth': 'm',
    }
    
    _var_mapping = {
        'topographic__elevation': 'node',
        'soil__depth': 'node',
    }
    
    _var_doc = {
        'topographic__elevation':
            'elevation of the ground surface relative to some datum; this field gets updated',
        'soil__depth':
            'elevation of the sediment surface relative to some datum; this field gets updated',
    }
    
    
    def __init__(self, grid, day = 24, morn = 4, eve = 15, diffusivity = 0.0001, **kwds):
        """Initialize TruckPassErosion.

        Parameters
        ----------
        grid : ModelGrid
            Landlab ModelGrid object
        day: int, defaults to 24 hr
            Length of day, hr
        morn : int, defaults to 4 hr
            Time at which trucks begin driving, hr
        eve : int, defaults to 15 hr
            Time at which trucks stop driving, hr
        diffusivity : float, array, or field name, defaults to 0.0001 m^2/hr
            Diffusivity of the sediment on road surface, m^2/hr
        """
        # Store grid and parameters
        self._grid = grid
        self.day = day
        self.morn = morn
        self.eve = eve
        self.diffusivity = diffusivity
        
        # Get elevation field
        try:
            self.elev = self.grid.at_node['topographic__elevation']
        except:
            raise
            
        # Get sediment field
        try:
            self.sed = self.grid.at_node['soil__depth']
        except:
            raise
               
        # Instantiate linear diffuser
        self.lin_diffuse1 = LinearDiffuser(grid, linear_diffusivity=self.diffusivity)
        #self.lin_diffuse2 = LinearDiffuser(grid, linear_diffusivity=self.diffusivity, \
        #                                   values_to_diffuse = 'soil__depth')
        
        #initialize truck pass and time arrays
        self.truck_pass = []
        self.time = []
		
    def run_one_step(self, tire_tracks, step, current_time = 0):    
        #initialize/reset the times for each loop
        self.t_recover = current_time
        self.t_pass = current_time
        self.t_total = current_time
        self.sed[tire_tracks] = 0      
        
        rng = np.random.RandomState(2024)

        while self.t_total <= self.day:
            if self.t_total < self.morn:
                self.T_B_morning = rng.random.exponential(self.morn)
                self.time.append(self.t_total + (self.day*step))
                self.truck_pass.append(0)
                self.t_recover += self.T_B_morning
            
            elif self.t_total >= self.morn and self.t_total <= self.eve:
                self.t_b = rng.random.exponential(2.2)
                
                self.sed[tire_tracks[0]] -= 0.001
                self.sed[tire_tracks[1]] -= 0.001
                self.sed[tire_tracks[2]] += 0.0004
                self.sed[tire_tracks[3]] += 0.0004
                self.sed[tire_tracks[4]] += 0.0004
                self.sed[tire_tracks[5]] += 0.0004
                self.sed[tire_tracks[6]] += 0.0002
                self.sed[tire_tracks[7]] += 0.0002
                               
                self.elev += self.sed
                self.time.append(self.t_total + (self.day*step))
                self.truck_pass.append(1)
                self.t_pass += self.t_b
                  
            elif self.t_total > self.eve:
                self.T_B_night = rng.random.exponential((self.day - self.eve))
                
                self.time.append(self.t_total + self.day*step)
                self.truck_pass.append(0)
                self.t_recover += self.T_B_night                
                self.lin_diffuse1.run_one_step(self.T_B_night)
                #self.lin_diffuse2.run_one_step(self.T_B_night)  
                
            self.t_total = self.t_pass + self.t_recover
			
        return(self.time, self.truck_pass)
