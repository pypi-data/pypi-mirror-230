
from typing import cast

from dataclasses import dataclass

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from untangle import Element

from pyutmodel.PyutField import PyutField
from pyutmodel.PyutField import PyutFields

from pyutmodel.PyutObject import PyutObject
from pyutmodel.PyutUseCase import PyutUseCase
from pyutmodel.PyutActor import PyutActor
from pyutmodel.PyutInterface import PyutInterface
from pyutmodel.PyutLink import PyutLink
from pyutmodel.PyutLinkType import PyutLinkType

from pyutmodel.PyutMethod import PyutMethods
from pyutmodel.PyutMethod import PyutParameters
from pyutmodel.PyutMethod import SourceCode
from pyutmodel.PyutParameter import PyutParameter
from pyutmodel.PyutMethod import PyutMethod
from pyutmodel.PyutMethod import PyutModifiers

from pyutmodel.PyutModifier import PyutModifier
from pyutmodel.PyutType import PyutType
from pyutmodel.PyutClass import PyutClass
from pyutmodel.PyutNote import PyutNote
from pyutmodel.PyutText import PyutText
from pyutmodel.PyutStereotype import PyutStereotype
from pyutmodel.PyutVisibilityEnum import PyutVisibilityEnum
from pyutmodel.PyutDisplayParameters import PyutDisplayParameters
from pyutmodel.PyutSDInstance import PyutSDInstance
from pyutmodel.PyutSDMessage import PyutSDMessage

from untanglepyut import XmlConstants

from untanglepyut.XmlVersion import XmlVersion
from untanglepyut.Common import secureInteger
from untanglepyut.Common import str2bool
from untanglepyut.Types import Elements


@dataclass
class ConvolutedPyutSDMessageInformation:
    """
    This class is necessary because I do not want to mix Ogl and PyutModel code;  Unfortunately,
    the IDs of the PyutSDInstance are buried and require a lookup

    """
    pyutSDMessage: PyutSDMessage = cast(PyutSDMessage, None)
    sourceId:      int           = -1
    destinationId: int           = -1


class UnTanglePyut:
    """
    Converts PyutModel Version 11 XML to Pyut Objects
    """
    # https://www.codetable.net/hex/a
    END_OF_LINE_MARKER: str = '&#xA;'

    def __init__(self, xmlVersion: XmlVersion):

        self.logger: Logger = getLogger(__name__)

        self._xmlVersion: XmlVersion = xmlVersion
        if self._xmlVersion == XmlVersion.V10:
            self._elementMethod:         str = XmlConstants.V10_ELEMENT_METHOD
            self._elementParameter:      str = XmlConstants.V10_ELEMENT_PARAMETER
            self._elementField:          str = XmlConstants.V10_ELEMENT_FIELD

            self._attrId:                str = XmlConstants.V10_ATTR_ID
            self._attrStereoType:        str = XmlConstants.V10_ATTR_STEREOTYPE
            self._attrDisplayMethods:    str = XmlConstants.V10_ATTR_DISPLAY_METHODS
            self._attrDisplayParameters: str = XmlConstants.V10_ATTR_DISPLAY_PARAMETERS
            self._attrDisplayFields:     str = XmlConstants.V10_ATTR_DISPLAY_FIELDS
            self._attrDisplayStereoType: str = XmlConstants.V10_ATTR_DISPLAY_STEREOTYPE

            self._attrCardinalitySource:      str = XmlConstants.V10_ATTR_CARDINALITY_SOURCE
            self._attrCardinalityDestination: str = XmlConstants.V10_ATTR_CARDINALITY_DESTINATION
            self._attrBidirectional:          str = XmlConstants.V10_ATTR_BIDIRECTIONAL
            self._attrSourceId:               str = XmlConstants.V10_ATTR_SOURCE_ID
            self._attrDestinationId:          str = XmlConstants.V10_ATTR_DESTINATION_ID
            self._attrSDMessageSourceId:      str = XmlConstants.V10_ATTR_SD_MESSAGE_SOURCE_ID
            self._attrSDMessageDestinationId: str = XmlConstants.V10_ATTR_SD_MESSAGE_DESTINATION_ID

            self._attrSourceTime:             str = XmlConstants.V10_ATTR_SOURCE_TIME
            self._attrDestinationTime:        str = XmlConstants.V10_ATTR_DESTINATION_TIME

            self._attrFileName: str = XmlConstants.V10_ATTR_FILENAME
        else:
            self._elementParameter      = XmlConstants.V11_ELEMENT_PARAMETER
            self._elementMethod         = XmlConstants.V11_ELEMENT_METHOD
            self._elementField          = XmlConstants.V11_ELEMENT_FIELD

            self._attrId                = XmlConstants.V11_ATTR_ID
            self._attrStereoType        = XmlConstants.V11_ATTR_STEREOTYPE
            self._attrDisplayMethods    = XmlConstants.V11_ATTR_DISPLAY_METHODS
            self._attrDisplayParameters = XmlConstants.V11_ATTR_DISPLAY_PARAMETERS
            self._attrDisplayFields     = XmlConstants.V11_ATTR_DISPLAY_FIELDS
            self._attrDisplayStereoType = XmlConstants.V11_ATTR_DISPLAY_STEREOTYPE

            self._attrCardinalitySource      = XmlConstants.V11_ATTR_CARDINALITY_SOURCE
            self._attrCardinalityDestination = XmlConstants.V11_ATTR_CARDINALITY_DESTINATION
            self._attrBidirectional          = XmlConstants.V11_ATTR_BIDIRECTIONAL
            self._attrSourceId               = XmlConstants.V11_ATTR_SOURCE_ID
            self._attrDestinationId          = XmlConstants.V11_ATTR_DESTINATION_ID
            self._attrSDMessageSourceId      = XmlConstants.V11_ATTR_SD_MESSAGE_SOURCE_ID
            self._attrSDMessageDestinationId = XmlConstants.V11_ATTR_SD_MESSAGE_DESTINATION_ID

            self._attrSourceTime             = XmlConstants.V11_ATTR_SOURCE_TIME
            self._attrDestinationTime        = XmlConstants.V11_ATTR_DESTINATION_TIME

            self._attrFileName = XmlConstants.V10_ATTR_FILENAME

    def classToPyutClass(self, graphicClass: Element) -> PyutClass:
        if self._xmlVersion == XmlVersion.V10:
            classElement: Element = graphicClass.Class
        elif self._xmlVersion == XmlVersion.V11:
            classElement = graphicClass.PyutClass
        else:
            assert False, f'Unsupported Xml Version {self._xmlVersion}'

        pyutClass: PyutClass = PyutClass()

        pyutClass = cast(PyutClass, self._addPyutObjectAttributes(pyutElement=classElement, pyutObject=pyutClass))

        displayParameters: PyutDisplayParameters = PyutDisplayParameters.toEnum(classElement[self._attrDisplayParameters])

        showStereotype:    bool = bool(classElement[self._attrDisplayStereoType])
        showFields:        bool = bool(classElement[self._attrDisplayFields])
        showMethods:       bool = bool(classElement[self._attrDisplayMethods])
        stereotypeStr:     str  = classElement[self._attrStereoType]

        pyutClass.displayParameters = displayParameters

        pyutClass.displayStereoType = showStereotype
        pyutClass.showFields        = showFields
        pyutClass.showMethods       = showMethods

        pyutClass.description = classElement['description']
        pyutClass.stereotype = PyutStereotype.toEnum(stereotypeStr)

        pyutClass.methods = self._methodToPyutMethods(classElement=classElement)
        pyutClass.fields  = self._fieldToPyutFields(classElement=classElement)

        return pyutClass

    def textToPyutText(self, graphicText: Element) -> PyutText:
        """
        Parses Text elements
        Args:
            graphicText:   Of the form:   <Text id="3" content="I am standalone text"/>

        Returns: A PyutText Object
        """
        if self._xmlVersion == XmlVersion.V10:
            textElement: Element  = graphicText.Text
        else:
            textElement = graphicText.PyutText

        pyutText:    PyutText = PyutText()

        pyutText.id  = textElement['id']

        rawContent:   str = textElement['content']
        cleanContent: str = rawContent.replace(UnTanglePyut.END_OF_LINE_MARKER, osLineSep)
        pyutText.content = cleanContent

        return pyutText

    def noteToPyutNote(self, graphicNote: Element) -> PyutNote:
        """
        Parse Note elements
        Args:
            graphicNote: of the form:  <Note id="2" content="I am a UML Note" filename=""/>

        Returns: A PyutNote Object
        """
        if self._xmlVersion == XmlVersion.V10:
            noteElement: Element = graphicNote.Note
        else:
            noteElement = graphicNote.PyutNote

        pyutNote: PyutNote = PyutNote()

        # fix line feeds
        pyutNote = cast(PyutNote, self._addPyutObjectAttributes(pyutElement=noteElement, pyutObject=pyutNote))

        rawContent:   str = noteElement['content']
        cleanContent: str = rawContent.replace(UnTanglePyut.END_OF_LINE_MARKER, osLineSep)
        pyutNote.content = cleanContent

        return pyutNote

    def interfaceToPyutInterface(self, oglInterface2: Element) -> PyutInterface:

        if self._xmlVersion == XmlVersion.V10:
            pyutInterfaceElement: Element = oglInterface2.Interface
        else:
            pyutInterfaceElement  = oglInterface2.PyutInterface

        interfaceId: int = int(pyutInterfaceElement['id'])
        name:        str = pyutInterfaceElement['name']
        description: str = pyutInterfaceElement['description']

        pyutInterface: PyutInterface = PyutInterface(name=name)
        pyutInterface.id          = interfaceId
        pyutInterface.description = description

        implementors: Element = pyutInterfaceElement.get_elements('Implementor')
        for implementor in implementors:
            pyutInterface.addImplementor(implementor['implementingClassName'])

        pyutInterface.methods = self._interfaceMethodsToPyutMethods(interface=pyutInterfaceElement)
        return pyutInterface

    def actorToPyutActor(self, graphicActor: Element) -> PyutActor:
        """

        Args:
            graphicActor:   untangle Element in the above format

        Returns:   PyutActor
        """
        if self._xmlVersion == XmlVersion.V10:
            actorElement: Element   = graphicActor.Actor
        else:
            actorElement = graphicActor.PyutActor

        pyutActor: PyutActor = PyutActor()

        pyutActor = cast(PyutActor, self._addPyutObjectAttributes(pyutElement=actorElement, pyutObject=pyutActor))

        return pyutActor

    def useCaseToPyutUseCase(self, graphicUseCase: Element) -> PyutUseCase:
        """

        Args:
            graphicUseCase:  An untangle Element in the above format

        Returns:  PyutUseCase
        """
        if self._xmlVersion == XmlVersion.V10:
            useCaseElement: Element     = graphicUseCase.UseCase
        else:
            useCaseElement = graphicUseCase.PyutUseCase

        pyutUseCase:    PyutUseCase = PyutUseCase()

        pyutUseCase = cast(PyutUseCase, self._addPyutObjectAttributes(pyutElement=useCaseElement, pyutObject=pyutUseCase))

        return pyutUseCase

    def linkToPyutLink(self, singleLink: Element, source: PyutClass, destination: PyutClass) -> PyutLink:
        linkTypeStr:     str          = singleLink['type']

        linkType:        PyutLinkType = PyutLinkType.toEnum(linkTypeStr)
        cardSrc:         str          = singleLink[self._attrCardinalitySource]
        cardDest:        str          = singleLink[self._attrCardinalityDestination]
        bidir:           bool         = str2bool(singleLink[self._attrBidirectional])
        linkDescription: str          = singleLink['name']

        pyutLink: PyutLink = PyutLink(name=linkDescription,
                                      linkType=linkType,
                                      cardSrc=cardSrc, cardDest=cardDest,
                                      bidir=bidir,
                                      source=source,
                                      destination=destination)

        return pyutLink

    def sdInstanceToPyutSDInstance(self, oglSDInstanceElement: Element) -> PyutSDInstance:

        if self._xmlVersion == XmlVersion.V10:
            instanceElement: Element = oglSDInstanceElement.SDInstance
        else:
            instanceElement = oglSDInstanceElement.PyutSDInstance
        pyutSDInstance:  PyutSDInstance = PyutSDInstance()

        pyutSDInstance.id                     = int(instanceElement['id'])
        pyutSDInstance.instanceName           = instanceElement['instanceName']
        pyutSDInstance.instanceLifeLineLength = secureInteger(instanceElement['lifeLineLength'])

        return pyutSDInstance

    def sdMessageToPyutSDMessage(self, oglSDMessageElement: Element) -> ConvolutedPyutSDMessageInformation:
        """
        TODO:  Need to fix how SD Messages are created
        Args:
            oglSDMessageElement:

        Returns:  Bogus data class
        """
        if self._xmlVersion == XmlVersion.V10:
            messageElement: Element = oglSDMessageElement.SDMessage
        else:
            messageElement = oglSDMessageElement.PyutSDMessage

        pyutSDMessage:  PyutSDMessage = PyutSDMessage()

        pyutSDMessage.id = int(messageElement['id'])
        pyutSDMessage.message = messageElement['message']
        pyutSDMessage.linkType = PyutLinkType.SD_MESSAGE

        srcID: int = int(messageElement[self._attrSDMessageSourceId])
        dstID: int = int(messageElement[self._attrSDMessageDestinationId])

        srcTime: int = int(messageElement[self._attrSourceTime])
        dstTime: int = int(messageElement[self._attrDestinationTime])

        pyutSDMessage.sourceY      = srcTime
        pyutSDMessage.destinationY = dstTime

        bogus: ConvolutedPyutSDMessageInformation = ConvolutedPyutSDMessageInformation()

        bogus.pyutSDMessage = pyutSDMessage
        bogus.sourceId      = srcID
        bogus.destinationId = dstID

        return bogus

    def _methodToPyutMethods(self, classElement: Element) -> PyutMethods:
        """
        The pyutClass may not have methods;
        Args:
            classElement:  The pyutClassElement

        Returns:  May return an empty list
        """
        untangledPyutMethods: PyutMethods = PyutMethods([])

        methodElements: Elements = classElement.get_elements(self._elementMethod)

        for methodElement in methodElements:
            methodName: str                = methodElement['name']
            visibility: PyutVisibilityEnum = PyutVisibilityEnum.toEnum(methodElement['visibility'])
            self.logger.debug(f"{methodName=} - {visibility=}")

            pyutMethod: PyutMethod = PyutMethod(name=methodName, visibility=visibility)

            pyutMethod.modifiers = self._modifierToPyutMethodModifiers(methodElement=methodElement)

            if self._xmlVersion == XmlVersion.V10:
                returnElement = methodElement.get_elements('Return')
                if len(returnElement) > 0:
                    pyutType: PyutType = PyutType(value=returnElement[0]['type'])
                    pyutMethod.returnType = pyutType
            elif self._xmlVersion == XmlVersion.V11:
                returnAttribute = methodElement['returnType']
                pyutMethod.returnType = PyutType(returnAttribute)
            else:
                assert False, f'Unsupported Xml Version {self._xmlVersion}'

            parameters = self._paramToPyutParameters(methodElement)
            pyutMethod.parameters = parameters
            pyutMethod.sourceCode = self._sourceCodeToPyutSourceCode(methodElement=methodElement)

            untangledPyutMethods.append(pyutMethod)

        return untangledPyutMethods

    def _fieldToPyutFields(self, classElement: Element) -> PyutFields:
        untangledPyutFields: PyutFields = PyutFields([])

        fieldElements: Elements = classElement.get_elements(self._elementField)

        for fieldElement in fieldElements:
            visibility:    PyutVisibilityEnum = PyutVisibilityEnum.toEnum(fieldElement['visibility'])
            if self._xmlVersion == XmlVersion.V10:
                paramElements: Elements           = fieldElement.get_elements('Param')
                assert len(paramElements) == 1, 'Curiously there should be only one'

                paramElement: Element = paramElements[0]
                fieldName:    str       = paramElement[XmlConstants.V10_ATTR_NAME]
                pyutType:     PyutType  = PyutType(paramElement[XmlConstants.V10_ATTR_TYPE])
                defaultValue: str       = paramElement[XmlConstants.V10_ATTR_DEFAULT_VALUE]
                if defaultValue is None:
                    defaultValue = ''
            elif self._xmlVersion == XmlVersion.V11:
                fieldName    = fieldElement[XmlConstants.V11_ATTR_NAME]
                pyutType     = PyutType(fieldElement[XmlConstants.V11_ATTR_TYPE])
                defaultValue = fieldElement[XmlConstants.V11_ATTR_DEFAULT_VALUE]
            else:
                assert False, f'Unsupported Xml Version {self._xmlVersion}'

            pyutField: PyutField = PyutField(name=fieldName, visibility=visibility, fieldType=pyutType, defaultValue=defaultValue)

            untangledPyutFields.append(pyutField)

        return untangledPyutFields

    def _modifierToPyutMethodModifiers(self, methodElement: Element) -> PyutModifiers:
        """
        Should be in this form:

            <Modifier name="Modifier1"/>
            <Modifier name="Modifier2"/>
            <Modifier name="Modifier3"/>
            <Modifier name="Modifier4"/>

        Args:
            methodElement:

        Returns:  PyutModifiers if not exist returns an empty
        """

        modifierElements = methodElement.get_elements('Modifier')

        pyutModifiers: PyutModifiers = PyutModifiers([])
        if len(modifierElements) > 0:
            for modifierElement in modifierElements:
                modifierName:           str       = modifierElement['name']
                pyutModifier: PyutModifier = PyutModifier(modifierTypeName=modifierName)
                pyutModifiers.append(pyutModifier)

        return pyutModifiers

    def _paramToPyutParameters(self, methodElement: Element) -> PyutParameters:

        parameterElements = methodElement.get_elements(self._elementParameter)

        untangledPyutMethodParameters: PyutParameters = PyutParameters([])
        for parameterElement in parameterElements:
            name:           str = parameterElement['name']
            defaultValue:   str = parameterElement['defaultValue']
            parameterType:  PyutType = PyutType(parameterElement['type'])

            pyutParameter: PyutParameter = PyutParameter(name=name, parameterType=parameterType, defaultValue=defaultValue)

            untangledPyutMethodParameters.append(pyutParameter)

        return untangledPyutMethodParameters

    def _sourceCodeToPyutSourceCode(self, methodElement: Element) -> SourceCode:

        sourceCodeElements = methodElement.get_elements('SourceCode')
        codeElements = sourceCodeElements[0].get_elements('Code')
        sourceCode: SourceCode = SourceCode([])
        for codeElement in codeElements:
            self.logger.debug(f'{codeElement.cdata=}')
            codeLine: str = codeElement.cdata
            sourceCode.append(codeLine)
        return sourceCode

    def _interfaceMethodsToPyutMethods(self, interface: Element) -> PyutMethods:

        pyutMethods: PyutMethods = self._methodToPyutMethods(interface)

        return pyutMethods

    def _addPyutObjectAttributes(self, pyutElement: Element, pyutObject: PyutObject) -> PyutObject:
        """

        Args:
            pyutElement:    pyutElement XML with common keys
            pyutObject:     The PyutObject to update

        Returns:  The updated pyutObject as
        """

        pyutObject.id       = int(pyutElement[self._attrId])    # TODO revisit this when we start using UUIDs
        pyutObject.name     = pyutElement['name']
        pyutObject.fileName = pyutElement[self._attrFileName]

        return pyutObject
