from pxr import Usd, UsdGeom, UsdSkel, Gf, Vt

def create_defaults(stage):
    xform = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(xform.GetPrim())
    stage.SetStartTimeCode(1.0)
    stage.SetEndTimeCode(10.0)
    UsdGeom.SetStageMetersPerUnit(stage, 0.01)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

def create_skel_root(stage):
    skel_root = UsdSkel.Root.Define(stage, "/World/Model")

    binding_api = UsdSkel.BindingAPI.Apply(skel_root.GetPrim())

    return binding_api


def create_skel(stage):
    skel = UsdSkel.Skeleton.Define(stage, "/World/Model/Skel")
    joints = ["Shoulder", "Shoulder/Elbow", "Shoulder/Elbow/Hand"]
    skel.CreateJointsAttr(joints)
    skel.CreateBindTransformsAttr([
        Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 2, 1)),
        Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 4, 1))
    ])
    skel.CreateRestTransformsAttr([
        Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 2, 1)),
        Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 2, 1))
    ])

    return skel


def create_mesh(stage, skel):
    mesh = UsdGeom.Mesh.Define(stage, "/World/Model/Arm")

    points = [
        (0.5, -0.5, 4), (-0.5, -0.5, 4), (0.5, 0.5, 4), (-0.5, 0.5, 4),
        (-0.5, -0.5, 0), (0.5, -0.5, 0), (-0.5, 0.5, 0), (0.5, 0.5, 0),
        (-0.5, 0.5, 2), (0.5, 0.5, 2), (0.5, -0.5, 2), (-0.5, -0.5, 2)
    ]
    mesh.CreatePointsAttr(points)

    face_vertex_indices = [
        2, 3, 1, 0,
        6, 7, 5, 4,
        8, 9, 7, 6,
        3, 2, 9, 8,
        10, 11, 4, 5,
        0, 1, 11, 10,
        7, 9, 10, 5,
        9, 2, 0, 10,
        3, 8, 11, 1,
        8, 6, 4, 11
    ]

    mesh.CreateFaceVertexIndicesAttr(face_vertex_indices)

    face_vertex_counts = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    mesh.CreateFaceVertexCountsAttr(face_vertex_counts)


    binding_api = UsdSkel.BindingAPI.Apply(mesh.GetPrim())

    binding_api.CreateSkeletonRel().SetTargets([skel.GetPath()])
    binding_api.CreateJointIndicesAttr([
        2,2,2,2, 0,0,0,0, 1,1,1,1
    ])
    binding_api.CreateJointIndicesPrimvar(False, 1)
    binding_api.CreateJointWeightsAttr([
        1,1,1,1, 1,1,1,1, 1,1,1,1
    ])
    binding_api.CreateJointWeightsPrimvar(False, 1)
    identity = Gf.Matrix4d().SetIdentity()
    binding_api.CreateGeomBindTransformAttr(identity)


def create_anim(stage, skel):
    anim = UsdSkel.Animation.Define(stage, skel.GetPath().AppendPath("Anim"))
    anim.CreateJointsAttr(["Shoulder/Elbow"])
    anim.CreateTranslationsAttr([(0,0,2)])
    anim.CreateScalesAttr([(1,1,1)])


    rotations = [
        Gf.Quatf(1, 0, 0, 0),
        Gf.Quatf(0.7071, 0.7071, 0, 0)
    ]
    times = [1, 10]

    # Set the rotation timesamples on the animation.
    rotations_attr = anim.GetRotationsAttr()

    for i, time in enumerate(times):
        rotations_attr.Set(Vt.QuatfArray([rotations[i]]), time)

    return anim

if __name__ == "__main__":

    stage = Usd.Stage.CreateNew("test-arm.usda")
    create_defaults(stage)
    skel_root_binding_api = create_skel_root(stage)
    skel = create_skel(stage)
    create_mesh(stage, skel)
    anim = create_anim(stage, skel)

    skel_root_binding_api.CreateAnimationSourceRel().SetTargets([anim.GetPath()])


    stage.Save()