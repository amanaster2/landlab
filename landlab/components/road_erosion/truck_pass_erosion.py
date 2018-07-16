"""
Purpose: Practice Landlab component building - Road Erosion Component
Author: Amanda Manaster
Date: 06/08/2018
"""

from landlab import Component
from landlab.components import LinearDiffuser
import random as rnd


class TruckPassErosion(Component):
    
    _name = 'TruckPassErosion'
    
    _input_var_names = (
        'topographic__elevation',
        'supply__elevation',
    )
    
    _output_var_names = (        
        'topographic__elevation',
        'supply__elevation',
    )
    
    _var_units = {
        'topographic__elevation': 'm',
        'supply__elevation': 'm',
    }
    
    _var_mapping = {
        'topographic__elevation': 'node',
        'supply__elevation': 'node',
    }
    
    _var_doc = {
        'topographic__elevation':
            'elevation of the ground surface relative to some datum; this field gets updated',
        'supply__elevation':
            'elevation of the "supply" surface relative to some datum; this field gets updated',
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
            self.elev = grid.at_node['topographic__elevation']
        except:
            raise
            
        # Get supply field
        try:
            self.supply = grid.at_node['supply__elevation']
        except:
            raise
            
        # Instantiate linear diffuser
        self.lin_diffuse = LinearDiffuser(grid, linear_diffusivity=self.diffusivity,
                                          method='simple', deposit=True)
        #initialize truck pass and time arrays
        self.truck_pass = []
        self.time = []
		
    def run_one_step(self, tire_tracks, step, current_time = 0):    

        #initialize/reset the times for each loop
        self.t_recover = current_time
        self.t_pass = current_time
        self.t_total = current_time
    
        while self.t_total <= self.day:
            if self.t_total < self.morn:
                self.T_B_morning = rnd.expovariate(1/self.morn)
                self.time.append(self.t_total+self.day*step)
                self.truck_pass.append(0)
                self.t_recover += self.T_B_morning
            
            elif self.t_total >= self.morn and self.t_total <= self.eve:
                self.t_b = rnd.expovariate(1/2.2)
                
                self.elev[tire_tracks[0]] -= 0.001
                self.elev[tire_tracks[1]] -= 0.001
                self.elev[tire_tracks[2]] += 0.0004
                self.elev[tire_tracks[3]] += 0.0004
                self.elev[tire_tracks[4]] += 0.0004
                self.elev[tire_tracks[5]] += 0.0004
                self.elev[tire_tracks[6]] += 0.0002
                self.elev[tire_tracks[7]] += 0.0002
                
                self.supply[tire_tracks[2]] += 0.0004
                self.supply[tire_tracks[3]] += 0.0004
                self.supply[tire_tracks[4]] += 0.0004
                self.supply[tire_tracks[5]] += 0.0004
                self.supply[tire_tracks[6]] += 0.0002
                self.supply[tire_tracks[7]] += 0.0002
                
                self.time.append(self.t_total+self.day*step)
                self.truck_pass.append(1)
                self.t_pass += self.t_b
                  
            elif self.t_total > self.eve:
                self.T_B_night = rnd.expovariate(1/(self.day-self.eve))
                self.lin_diffuse.run_one_step(self.T_B_night)
                self.time.append(self.t_total+self.day*step)
                self.truck_pass.append(0)
                self.t_recover += self.T_B_night                
            
            self.t_total = self.t_pass + self.t_recover
			
        return(self.time, self.truck_pass)
