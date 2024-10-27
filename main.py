import RT_utility as rtu
import RT_camera as rtc
import RT_renderer as rtren
import RT_material as rtm
import RT_scene as rts
import RT_object as rto
import RT_integrator as rti
import RT_light as rtl
import RT_texture as rtt

def renderDoF():
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 480
    main_camera.center = rtu.Vec3(0,0,0)
    main_camera.samples_per_pixel = 222
    main_camera.max_depth = 5
    main_camera.vertical_fov = 60
    main_camera.look_from = rtu.Vec3(-2, 2, 1)
    main_camera.look_at = rtu.Vec3(0, 0, -1)
    main_camera.vec_up = rtu.Vec3(0, 1, 0)

    aperture = 1.0
    focus_distance = 0.5
    main_camera.init_camera(aperture, focus_distance)
    # add objects to the scene

    tex_earth = rtt.ImageTexture("./textures/KU_Symbol_Thai.jpg")
    mat_tex_earth = rtm.TextureColor(tex_earth)        # earth texture

    mat_metal1 = rtm.Metal(rtu.Color(1.0,0.50588,0.6588), 0.0001)
    mat_metal2 = rtm.Metal(rtu.Color(0.51372,0.13725,1.0), 0.0005)
    mat_metal3 = rtm.Metal(rtu.Color(0.0,1.0,1.0), 0.05)
    mat_metal4 = rtm.Metal(rtu.Color(1.0,0.48627,0.1392), 0.1)
    mat_metal5 = rtm.Metal(rtu.Color(0.8,0.8,0.8), 0.8)
    mat_metal6 = rtm.Metal(rtu.Color( 1, 1, 1), 1)

    mat_mirror = rtm.Mirror(rtu.Color(1,1,1))

    world = rts.Scene()
    world.add_object(rto.Quad(rtu.Vec3(-20, -1, -20), rtu.Vec3(50, 0, 0), rtu.Vec3(0, 0, 50), mat_tex_earth))
    world.add_object(rto.Sphere(rtu.Vec3(   0,   0.0,-1),  0.5, mat_metal1))
    world.add_object(rto.Sphere(rtu.Vec3(-1.0,   0.0,-1),  0.5, mat_metal2))
    world.add_object(rto.Sphere(rtu.Vec3( 1.0,   0.0,-1),  0.5, mat_metal3))
    world.add_object(rto.Sphere(rtu.Vec3( 2.0,   0.0,-1),  0.5, mat_metal4))
    world.add_object(rto.Sphere(rtu.Vec3( 3.0,   0.0,-1),  0.5, mat_metal5))
    world.add_object(rto.Sphere(rtu.Vec3( 4.0,   0.0,-1),  0.5, mat_metal6))

    point_light = rtl.Diffuse_light(rtu.Color(1.0, 1.0, 1.0))

    world.add_object(rto.Quad(rtu.Vec3(0, 3, -1), rtu.Vec3(10, 5, 1), rtu.Vec3(1, 5, -10), point_light))

    intg = rti.Integrator(bSkyBG=True)

    renderer = rtren.Renderer(main_camera, intg, world)
    renderer.render()
    renderer.write_img2png('week10_no_jitter_DoF.png')
    
    renderer.render_jittered()
    renderer.write_img2png('week10_jitter_DoF.png')

def renderMoving():
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 320
    main_camera.center = rtu.Vec3(0,0,0)
    main_camera.samples_per_pixel = 200
    main_camera.max_depth = 5
    main_camera.vertical_fov = 60
    main_camera.look_from = rtu.Vec3(-2, 2, 1)
    main_camera.look_at = rtu.Vec3(0, 0, -1)
    main_camera.vec_up = rtu.Vec3(0, 1, 0)

    defocus_angle = 0.0
    focus_distance = 5.0
    main_camera.init_camera(defocus_angle, focus_distance)
    # add objects to the scene

    tex_checker_bw = rtt.CheckerTexture(0.32, rtu.Color(.2, .2, .2), rtu.Color(.9, .9, .9))

    mat_tex_checker_bw = rtm.TextureColor(tex_checker_bw)

    mat_blinn1 = rtm.Blinn(rtu.Color(0.8, 0.5, 0.8), 0.5, 0.2, 8)
    mat_blinn2 = rtm.Blinn(rtu.Color(0.4, 0.5, 0.4), 0.5, 0.6, 8)
    mat_blinn3 = rtm.Blinn(rtu.Color(0.8, 0.5, 0.4), 0.5, 0.2, 8)


    sph_left = rto.Sphere(rtu.Vec3(-1.0,   0.0,-1),  0.5, mat_blinn1)
    sph_left.add_moving(rtu.Vec3(-1.0,   0.0,-1) + rtu.Vec3(0.0, 0.5,0.0))

    world = rts.Scene()
    world.add_object(rto.Sphere(rtu.Vec3(   0,-100.5,-1),  100, mat_tex_checker_bw))
    world.add_object(sph_left)    # left
    world.add_object(rto.Sphere(rtu.Vec3(   0,   0.0,-1),  0.5, mat_blinn2))    # center
    world.add_object(rto.Sphere(rtu.Vec3( 1.0,   0.0,-1),  0.5, mat_blinn3))    # right

    intg = rti.Integrator(bSkyBG=True)

    renderer = rtren.Renderer(main_camera, intg, world)
    renderer.render_jittered()
    renderer.write_img2png('week10_moving_nojitter.png')    


def render():
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 320
    main_camera.center = rtu.Vec3(0,0,0)
    main_camera.samples_per_pixel = 100
    main_camera.max_depth = 5
    main_camera.vertical_fov = 60
    main_camera.look_from = rtu.Vec3(-2, 2, 1)
    main_camera.look_at = rtu.Vec3(0, 0, -1)
    main_camera.vec_up = rtu.Vec3(0, 1, 0) 

    defocus_angle = 0.0
    focus_distance = 5.0
    main_camera.init_camera(defocus_angle, focus_distance)

    world = rts.Scene()

    light_color = rtu.Color(1.0, 1.0, 1.0)
    light_mat = rtl.Diffuse_light(light_color)
    world.add_object(rto.Quad(rtu.Vec3(-2, 5, -2),
                              rtu.Vec3(4, 0, 0),
                              rtu.Vec3(0, 0, 4),
                              light_mat))
    world.add_object(rto.Quad(rtu.Vec3(-5, 2, 0),
                             rtu.Vec3(0, 2, 0),
                             rtu.Vec3(0, 0, 2),
                             light_mat))
    




    intg = rti.Integrator(bSkyBG=True)

    renderer = rtren.Renderer(main_camera, intg, world)
    renderer.render_jittered()
    renderer.write_img2png('test.png')   

def renderVolume():

    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 320
    main_camera.center = rtu.Vec3(0,0,0)
    main_camera.samples_per_pixel = 100
    main_camera.max_depth = 5
    main_camera.vertical_fov = 60
    main_camera.look_from = rtu.Vec3(-2, 2, 1)
    main_camera.look_at = rtu.Vec3(0, 0, -1)
    main_camera.vec_up = rtu.Vec3(0, 1, 0) 

    defocus_angle = 0.0
    focus_distance = 5.0
    main_camera.init_camera(defocus_angle, focus_distance)

    scene = rts.Scene()

    # Create a fog volume inside a box
    box_boundary = rto.Box(
    rtu.Vec3(-100, 0, -100),    # Min point
    rtu.Vec3(100, 50, 100),     # Max point
    )

    fog_volume = rto.ConstantMedium(
    boundary=box_boundary,    
    density=0.5,             # Dense fog
    color=rtu.Color(0.2,0.2,0.2)       # Pure white
    )

    scene.add_object(fog_volume)

    # Create smoke volume inside a sphere
    sphere_boundary = rto.Sphere(
        rtu.Vec3(0, 5, 0),         # Center
        5.0                         # Radius
    )

    smoke_density = 0.1
    smoke_color = rtu.Color(0.2, 0.2, 0.2)
    smoke_volume = rto.ConstantMedium(sphere_boundary, smoke_density, smoke_color)
    scene.add_object(smoke_volume)

    # Use the volume integrator instead of regular integrator
    intg = rti.VolumeIntegrator(bDlight=True, bSkyBG=True)

    renderer = rtren.Renderer(main_camera, intg, scene)
    renderer.render_jittered()
    renderer.write_img2png('test.png')   

def renderVolume2():
    # Camera setup
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 360  # Higher resolution
    main_camera.samples_per_pixel = 100
    main_camera.max_depth = 50   # Increased for better volume effects
    main_camera.vertical_fov = 60
    # Position camera to better see volumes
    main_camera.look_from = rtu.Vec3(0, 10, 20)  # Higher and further back
    main_camera.look_at = rtu.Vec3(0, 5, 0)      # Looking at smoke sphere
    main_camera.vec_up = rtu.Vec3(0, 1, 0)
    main_camera.init_camera(0.0, 10.0)  # Increased focus distance

    # Create scene
    scene = rts.Scene(rtu.Color(0.7, 0.8, 1.0))  # Light blue sky background

    # # Add ground plane
    # ground = rto.Quad(
    #     rtu.Vec3(-100, 0, -100),
    #     rtu.Vec3(200, 0, 0),
    #     rtu.Vec3(0, 0, 200),
    #     rtm.Lambertian(rtu.Color(0.5, 0.5, 0.5))
    # )
    # scene.add_object(ground)

    # Add light source
    light = rto.Sphere(
        rtu.Vec3(0, 30, 0),  # Light above scene
        5.0,                 # Large light for soft shadows
        rtl.Diffuse_light(rtu.Color(1.0, 1.0, 1.0))  # Bright white light
    )
    scene.add_object(light)

    # # Create fog volume
    # box_boundary = rto.Box(
    #     rtu.Vec3(-20, 0, -20),    # Smaller box
    #     rtu.Vec3(20, 15, 20),     # Not as tall
    # )
    # fog_volume = rto.ConstantMedium(
    #     boundary=box_boundary,    
    #     fDensity=0.05,            # Less dense for better visibility
    #     cAlbedo=rtu.Color(0.8, 0.8, 0.8)  # Lighter color
    # )
    # scene.add_object(fog_volume)

    # Create smoke volume
    sphere_boundary = rto.Sphere(
        rtu.Vec3(0, 8, 10),        # Raised up
        4.0                       # Slightly smaller
    )
    smoke_volume = rto.ConstantMedium(
        boundary=sphere_boundary,
        fDensity=0.2,             # Denser than fog
        cAlbedo=rtu.Color(0.1, 0.1, 0.1)  # Dark smoke
    )
    scene.add_object(smoke_volume)

    # # Add some objects in the volumes for interest
    # metal_sphere1 = rto.Sphere(
    #     rtu.Vec3(-3, 2, 0),
    #     1.0,
    #     rtm.Metal(rtu.Color(0.8, 0.3, 0.3), 0.0)  # Red metal
    # )
    # scene.add_object(metal_sphere1)

    # metal_sphere2 = rto.Sphere(
    #     rtu.Vec3(3, 2, 0),
    #     1.0,
    #     rtm.Metal(rtu.Color(0.3, 0.3, 0.8), 0.0)  # Blue metal
    # )
    # scene.add_object(metal_sphere2)

    # Use volume integrator
    intg = rti.VolumeIntegrator(bDlight=True, bSkyBG=True)
    renderer = rtren.Renderer(main_camera, intg, scene)
    
    # Render
    renderer.render_jittered()
    renderer.write_img2png('volume_scene.png')

if __name__ == "__main__":
    renderVolume2()


