from Snoopy import logger
from Snoopy.PyplotTools import vtkLookupTable_from_cmap

def viewPolyData( polydata, *, cellFieldName = None, pointFieldName = None,
                  component = None, cmap = "Blues", use_osp = False):
    """Create the renderer to quickly visualze a mesh.

    Parameters
    ----------
    polydata : vtkPolyData
        The mesh to visualize.

    cellFieldName : str or None, optional
        Color by cell values. The default is None.
    pointFieldName : str or None, optional
        Color by node values. The default is None.
    component : int or None, optional
        Component in case field has several ones. The default is None.
    cmap : str, optional
        colormap, matplotlib label. The default is "Blues".
    use_osp : bool, optional
        Whether to use ray tracing. The default is False.
    """
    import vtk
    
    
    actor = getPolydataActor(  polydata, cellFieldName = cellFieldName, pointFieldName=pointFieldName, 
                               component = component, 
                               cmap = cmap )

    actor.GetProperty().SetMetallic(1.0)
    actor.GetProperty().SetColor(0.5, 0.5, 0.5)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)  # White background

    if use_osp :
        print("Using ospray")
        osprayPass = vtk.vtkOSPRayPass()

        renderer.SetPass(osprayPass)

        osprayNode = vtk.vtkOSPRayRendererNode()
        osprayNode.SetEnableDenoiser(1, renderer)

        osprayNode.SetSamplesPerPixel(4,renderer)
        osprayNode.SetAmbientSamples(0,renderer)
        osprayNode.SetMaxFrames(4, renderer)

        osprayNode.SetRendererType("pathtracer", renderer);

        osprayNode.SetBackgroundMode(osprayNode.Environment, renderer)

        renderer.SetEnvironmentUp( -1 , 0. , 0.0)
        renderer.SetEnvironmentRight( 0 , -1 , 0)

        renderer.SetEnvironmentalBG(0.0, 0.9, 0.0)
        renderer.SetEnvironmentalBG2(0.0, 0.9, 0.0)
        renderer.GradientEnvironmentalBGOn()

        ml = vtk.vtkOSPRayMaterialLibrary()
        ml.AddMaterial("metal_1", "thinGlass")
        ml.AddShaderVariable("metal_1", "attenuationColor", 3,  [ 0.0, 0.9, 0.0 ])

        osprayNode.SetMaterialLibrary(ml, renderer)

        actor.GetProperty().SetMaterialName("metal_1")

        actor.GetProperty().SetEdgeVisibility(1)


    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(800, 600)
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.SetInteractorStyle( vtk.vtkInteractorStyleTrackballCamera() )

    renderer.AddActor(actor)
    renderWindow.Render()
    renderWindowInteractor.Start()


def getPolydataActor( polydata, *, cellFieldName = None, pointFieldName = None, component = None, cmap = "Blues" ):
    import vtk

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData( polydata )

    if cellFieldName is not None :
        cd = polydata.GetCellData()
        available_field = [ cd.GetArrayName(i) for i in range(cd.GetNumberOfArrays()) ]
        if cellFieldName not in available_field : 
            logger.warning( f"{cellFieldName:} not available in {available_field:}" )
        
        mapper.SetLookupTable( vtkLookupTable_from_cmap( cmap ) )
        mapper.SetScalarModeToUseCellFieldData()
        mapper.SelectColorArray( cellFieldName )
        
    elif pointFieldName is not None :
        pd = polydata.GetPointData()
        available_field = [ pd.GetArrayName(i) for i in range(pd.GetNumberOfArrays()) ]
        if pointFieldName not in available_field : 
            logger.warning( f"{pointFieldName:} not available in {available_field:}" )
        
        mapper.SetLookupTable( vtkLookupTable_from_cmap( cmap ) )
        mapper.SetColorModeToMapScalars()
        mapper.SetScalarModeToUsePointFieldData()
        mapper.SelectColorArray( pointFieldName )
        
    if component is not None:
        mapper.GetLookupTable().SetVectorComponent(component)
        
    mapper.SetUseLookupTableScalarRange(False)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetEdgeVisibility(1)
    return actor


def polydataPicture( polydata, *, cellFieldName = None, cmap = "Blues", outputFile ):
    import vtk
    w2if = vtk.vtkRenderLargeImage()
    #w2if.SetMagnification(4)   # => Resoulition of the picture

    actor = getPolydataActor(  polydata, cellFieldName = cellFieldName, cmap = cmap )

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(800, 600)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)  # White background
    renderer.AddActor(actor)
    renderWindow.AddRenderer(renderer)


    w2if.SetInput(renderer)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(outputFile)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()

