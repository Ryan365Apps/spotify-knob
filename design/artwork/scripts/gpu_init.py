import bpy
p=bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type='HIP'
p.get_devices()
for d in p.devices: d.use=(d.type=='HIP')
bpy.data.scenes['TEASER'].cycles.device='GPU'
