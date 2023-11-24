from manim import *
import numpy as np

def get_angle_by_value(value, max_value):
    return (2 * value  / max_value - 1) * np.pi
def position_by_value(value, max_value):
    angle = get_angle_by_value(value, max_value)
    return np.array([np.sin(angle), np.cos(angle), 0])


class knob:
    def __init__(self, pos, radius, color, title, init_value = 0, max_value = 1024):
        self.crs = Circle(radius, color = color)
        self.radius = radius
        self.max_value = max_value
        self.crs.move_to(pos)
        self.angle = get_angle_by_value(init_value, max_value)
        self.line = Line(pos, pos + position_by_value(init_value, max_value) * radius)
        self.title = Text(title).move_to(self.crs.get_center() - np.array([0, radius + 0.2, 0])).scale(0.6)
        self.center_circle = Circle(radius / 10, color = WHITE, fill_opacity = 1).move_to(pos)
        self.knob_vmobject = Group(self.line, self.crs, self.title, self.center_circle)
    def create_knob(self):
        return Create(self.crs), Create(self.line), Create(self.title), Create(self.center_circle)
    def set_value(self, value):
        prev_angle = self.angle
        self.angle = get_angle_by_value(value, self.max_value)
        return Rotate(self.line, angle = prev_angle - self.angle, about_point = self.crs.get_center())    

class Patch_point:
    def __init__(self, radius, color, title, position):
        self.big_circle = Circle(radius, color = color).move_to(position)
        self.small_circle = Circle(radius / 2, color = color).move_to(position)
        self.title = Text(title).move_to(position - np.array([0, radius + 0.5 * radius, 0])).scale(0.8 * radius + 0.1)
        self.patch_point_vmobject = Group(self.big_circle, self.small_circle, self.title)
    def create(self):
        return Create(self.big_circle), Create(self.small_circle), Create(self.title)    


class VCO:
    def __init__(self, width, height, position):
        self.knob_positions = {'freq': [position[0], height / 3 + position[1], 0],
                               'pw': [position[0] - width / 4, position[1], 0],
                               'fm': [position[0] + width / 4, position[1], 0]}
        self.knob_radius = {'freq': 0.8 * width / 2, 'pw': 0.35 * width / 2, 'fm': 0.35 * width / 2}
        self.knob_colors = {'freq': BLUE, 'pw': BLUE, 'fm': BLUE}
        self.knob_max_values = {'freq': 1024, 'pw': 100, 'fm': 100}
        self.kbob_initials = {'freq': 440, 'pw': 50, 'fm': 50}
        limit_patch_point = width / 8
        patch_point_radius = 0.06 * width
        self.patch_point_positions = {'1v/oct': [limit_patch_point + position[0] - width / 2, position[1] - height / 2 + height / 5, 0],
                                      'fm': [2 * limit_patch_point + position[0] - width / 2 + patch_point_radius * 2, position[1] - height / 2 + height / 5, 0],
                                      'sync': [3 * limit_patch_point + position[0] - width / 2 + patch_point_radius * 4, position[1] - height / 2 + height / 5, 0],
                                      'pw': [4 * limit_patch_point + position[0] - width / 2 + patch_point_radius * 6, position[1] - height / 2 + height / 5, 0],
                                      'sin': [limit_patch_point + position[0] - width / 2, position[1] - height / 2 + height / 10, 0],
                                      'tri': [2 * limit_patch_point + position[0] - width / 2 + patch_point_radius * 2, position[1] - height / 2 + height / 10, 0],
                                      'rect': [3 * limit_patch_point + position[0] - width / 2 + patch_point_radius * 4, position[1] - height / 2 + height / 10, 0],
                                      'saw': [4 * limit_patch_point + position[0] - width / 2 + patch_point_radius * 6, position[1] - height / 2 + height / 10, 0]}
        self.patch_points = {key: Patch_point(patch_point_radius, color = WHITE, title = key, position = self.patch_point_positions[key]) for key in self.patch_point_positions.keys()}
        self.knobs = {key: knob(self.knob_positions[key], 
                                radius = self.knob_radius[key], 
                                title = key, 
                                color = self.knob_colors[key],
                                init_value = self.kbob_initials[key],
                                max_value = self.knob_max_values[key]) for key in self.knob_positions.keys()}
        self.surface_rect = Rectangle(color = WHITE, width = width, height = height).move_to(position)
        all_obj = [k.knob_vmobject for k in self.knobs.values()]
        print(all_obj)
        all_obj += [patch_point.patch_point_vmobject for patch_point in self.patch_points.values()]
        all_obj += [self.surface_rect]
        self.VCO_vmobject = Group(*all_obj)
    def create(self):
        module_creation = [Create(self.surface_rect)]
        for key in self.knobs.keys():
            for creation in self.knobs[key].create_knob():
                module_creation.append(creation)
        for key in self.patch_points.keys():
            for creation in self.patch_points[key].create():
                module_creation.append(creation)
        return module_creation

class Scope:
    def __init__(self, width, height, pos):
        self.axes = Axes(
            x_range=[-0.2, 0.2, 0.005],
            y_range=[-1.5, 1.5, 0.2],
            x_length=width - width / 4,
            y_length=height - height / 4,
            axis_config={"color": BLUE}
        ).move_to(pos + np.array([0.2, 0, 0]))
        self.surface = Rectangle(width = width, height = height).move_to(pos)
        self.inside_area = Rectangle(width = width - width / 4, height = height - height / 4).move_to(pos + np.array([0.2, 0, 0]))
        self.input_x = Patch_point(0.2, WHITE, 'ch1', pos - np.array([width / 2 - 0.4, height / 2 - 0.4, 0]))
        self.input_y = Patch_point(0.2, WHITE, 'ch2', pos - np.array([width / 2 - 0.4, height / 2 - 1.2, 0]))
        self.scope_vmobject = Group(self.surface, self.input_x.patch_point_vmobject, self.input_y.patch_point_vmobject, self.inside_area, self.axes)
    def cretae(self):
        creation = [Create(self.surface), Create(self.inside_area), Create(self.axes)]
        for y in self.input_x.create():
            creation.append(y)
        for y in self.input_y.create():
            creation.append(y)
        return creation
    def plot_signal(self, signal, updater, color = ORANGE):
        signal = self.axes.plot(signal, color = color)
        signal.add_updater(lambda m: m.become(self.axes.plot(updater, color = color)))
        return signal
    



def patch(k1, k2, color):
    cable = ArcBetweenPoints(k1.small_circle.get_center(), k2.small_circle.get_center(), color = color)
    start_circle = Circle(k1.small_circle.get_radius(), color = color, fill_opacity = 1).move_to(k1.small_circle.get_center())
    end_circle = Circle(k2.small_circle.get_radius(), color = color, fill_opacity = 1).move_to(k2.small_circle.get_center())
    return cable, start_circle, end_circle

def Create_patch(cable):
    return Create(cable[0]), Create(cable[1]), Create(cable[2])


class example(Scene):
    def construct(self):
        v = VCO(2, 6, np.zeros(3))
        v.VCO_vmobject.scale(1.2)
        s = Scope(5, 4, [2.5, 0, 0])
        s.scope_vmobject.scale(1.5)
        self.play(*v.create(), run_time = 1.4)        
        self.wait()
        self.play(v.VCO_vmobject.animate.shift(LEFT * 3))
        self.play(*s.cretae())
        cable_sin_scope = patch(v.patch_points['sin'], s.input_x, ORANGE)
        self.play(*Create_patch(cable_sin_scope))
        updator = lambda x: np.sin(2 * np.pi * float(freq_value.get_value()) * x + 0)
        freq_value = ValueTracker(10)
        signal = s.plot_signal(lambda x: np.sin(2 * np.pi * float(freq_value.get_value()) * x + 0), updator)
        self.play(Create(signal))
        self.wait()
        self.play(Indicate(v.knobs['freq'].knob_vmobject))
        self.wait()
        self.play(freq_value.animate.set_value(20 + 6),
                  v.knobs['freq'].set_value(440 + 100),
                  run_time= 2)
        self.play(freq_value.animate.set_value(20 - 3),
                  v.knobs['freq'].set_value(440 - 50),
                  run_time= 2)
        self.wait()
        v2 = VCO(2, 6, np.zeros(3))
        v2.VCO_vmobject.scale(1.2).shift(5.5 * LEFT)
        self.play(*v2.create())
        self.play(v2.knobs['freq'].set_value(45))
        self.wait()
        patch_sin_fm = patch(v2.patch_points['sin'], v.patch_points['fm'], color = PURPLE)
        patch_v2_osc = patch(v2.patch_points['sin'], s.input_y, color = RED)
        self.play(*Create_patch(patch_sin_fm), *Create_patch(patch_v2_osc))
        self.wait()
        depth = ValueTracker(0)
        time = ValueTracker(-0.2)
        self.remove(signal)
        modulator_signal = lambda x: np.sin(2 * np.pi * 3.5 * x) * (x < time.get_value())
        signal = s.plot_signal(lambda x: np.sin(2 * np.pi * float(freq_value.get_value() + freq_value.get_value() * depth.get_value() * modulator_signal(time.get_value() - 0.01)) * x + 0), 
                               lambda x: np.sin(2 * np.pi * float(freq_value.get_value() + freq_value.get_value() * depth.get_value() * modulator_signal(time.get_value() - 0.01)) * x + 0))
        signal2 = s.plot_signal(modulator_signal,
                                modulator_signal,
                                color = RED)
        self.add(signal)
        self.play(Create(signal2))
        self.play(time.animate.set_value(-0.05),
                  run_time = 2)
        self.wait()
        self.play(Indicate(v.knobs['fm'].knob_vmobject))
        self.play(v.knobs['fm'].set_value(80),
                  depth.animate.set_value(0.9),
                  time.animate.set_value(0.2),
                  run_time = 10)
        

    
    