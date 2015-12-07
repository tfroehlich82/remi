"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import remi.gui as gui
from remi import start, App
import math
from threading import Timer
import random

class SvgPlot(gui.Svg):
    def __init__(self, width, height):
        super(SvgPlot, self).__init__(width, height)
        self.width = width
        self.height = height
        self.polyList = []
        self.font_size = 15
        self.plot_inner_border = self.font_size
        self.textYMin = gui.SvgText(0,0,"min")
        self.textYMax = gui.SvgText(0,self.height + self.font_size,"max")
        self.textYMin.style['font-size'] = gui.to_pix(self.font_size)
        self.textYMax.style['font-size'] = gui.to_pix(self.font_size)
        self.append( str(id(self.textYMin)), self.textYMin )
        self.append( str(id(self.textYMax)), self.textYMax )
        
    def append_poly(self, poly):
        self.append(str(id(poly)), poly)
        self.polyList.append(poly)
        poly.textXMin = gui.SvgText(0,0,"actualValue")
        poly.textXMax = gui.SvgText(0,0,"actualValue")
        poly.textYVal = gui.SvgText(0,0,"actualValue")
        poly.textYVal.style['font-size'] = gui.to_pix(self.font_size)

        poly.lineYValIndicator = gui.SvgLine(0,0,0,0)
        poly.lineXMinIndicator = gui.SvgLine(0,0,0,0)
        poly.lineXMaxIndicator = gui.SvgLine(0,0,0,0)
        self.append( str(id(poly.textXMin)), poly.textXMin )
        self.append( str(id(poly.textXMax)), poly.textXMax )
        self.append( str(id(poly.textYVal)), poly.textYVal )
        self.append( str(id(poly.lineYValIndicator)), poly.lineYValIndicator )
        self.append( str(id(poly.lineXMinIndicator)), poly.lineXMinIndicator )
        self.append( str(id(poly.lineXMaxIndicator)), poly.lineXMaxIndicator )

    def remove_poly(self, poly):
        self.remove(poly)
        self.polyList.remove(poly)
        self.remove(poly.textXMin)
        self.remove(poly.textXMax)
        self.remove(poly.textYVal)
    
    def render(self):
        
        self.set_viewbox(-self.plot_inner_border, -self.plot_inner_border, self.width + self.plot_inner_border*2, self.height + self.plot_inner_border*2)
        if len(self.polyList)<1:
            return
        minX = min(self.polyList[0].coordsX)
        maxX = max(self.polyList[0].coordsX)
        minY = min(self.polyList[0].coordsY)
        maxY = max(self.polyList[0].coordsY)
        
        for poly in self.polyList:
            minX = min(minX, min(poly.coordsX))
            maxX = max(maxX, max(poly.coordsX))
            minY = min(minY, min(poly.coordsY))
            maxY = max(maxY, max(poly.coordsY))
        self.textYMin.set_text( "min:%s"%minY )
        self.textYMax.set_text( "max:%s"%maxY )

        scaleWidth = 1.0
        scaleHeight = 1.0
        if (maxX>minX):
            scaleWidth = self.width/float(abs(maxX-minX))
        if (maxY>minY):
            scaleHeight = self.height/float(abs(maxY-minY))

        i = 1
        for poly in self.polyList:
            scaledTranslatedYpos = (poly.coordsY[-1]-minY)*scaleHeight

            textXpos = self.height/(len(self.polyList)+1)*i

            poly.textXMin.set_text( str(min(poly.coordsX)) )
            poly.textXMin.set_fill( poly.style['stroke'])
            #poly.textXMin.set_position( -scaledTranslatedYpos, (min(poly.coordsX)-minX)*scaleWidth )
            poly.textXMin.set_position( -textXpos, (min(poly.coordsX)-minX)*scaleWidth )
            poly.textXMin.attributes['transform']="rotate(%s)"%(-90)
            poly.textXMax.set_text( str(max(poly.coordsX)) )
            poly.textXMax.set_fill( poly.style['stroke'])
            poly.textXMax.set_position( -textXpos, (max(poly.coordsX)-minX)*scaleWidth )
            #poly.textXMax.set_position( -scaledTranslatedYpos, (maxX-minX)*scaleWidth )
            poly.textXMax.attributes['transform']="rotate(%s)"%(-90)
            poly.textYVal.set_text( str(poly.coordsY[-1]) )
            poly.textYVal.set_fill( poly.style['stroke'])
            poly.textYVal.set_position( 0, scaledTranslatedYpos )
            #poly.textYVal.set_position( (maxX-minX)*scaleWidth/2.0, scaledTranslatedYpos )
                        
            poly.lineYValIndicator.set_stroke(1,poly.style['stroke'])
            poly.lineXMinIndicator.set_stroke(1,poly.style['stroke'])
            poly.lineXMaxIndicator.set_stroke(1,poly.style['stroke'])
            poly.lineYValIndicator.set_coords(0,scaledTranslatedYpos,self.width,scaledTranslatedYpos)
            poly.lineXMinIndicator.set_coords((min(poly.coordsX)-minX)*scaleWidth,0,(min(poly.coordsX)-minX)*scaleWidth,self.height)
            poly.lineXMaxIndicator.set_coords((max(poly.coordsX)-minX)*scaleWidth,0,(max(poly.coordsX)-minX)*scaleWidth,self.height)
            poly.attributes['transform']=('translate(%s,%s)'%(-minX*scaleWidth,-minY*scaleHeight) + ' scale(%s,%s)'%((scaleWidth),(scaleHeight)))

            i = i + 1


class MyApp(App):

    def __init__(self, *args):
        super(MyApp, self).__init__(*args)

    def main(self, name='world'):
        self.wid = gui.Widget(620, 620, False, 10)
        
        self.svgplot = SvgPlot(600,600)
        self.plotData1 = gui.SvgPolyline()
        self.plotData1.set_stroke(0.05,'rgba(255,0,0,0.8)')
        self.plotData1.set_max_len(500)
        self.plotData2 = gui.SvgPolyline()
        self.plotData2.set_stroke(0.05,'green')
        self.plotData2.set_max_len(500)
        self.plotData3 = gui.SvgPolyline()
        self.plotData3.set_stroke(0.05,'orange')
        self.plotData3.set_max_len(300)
        self.svgplot.append_poly( self.plotData1 )
        self.svgplot.append_poly( self.plotData2 )
        self.svgplot.append_poly( self.plotData3 )
        
        self.wid.append('plot', self.svgplot)
        
        self.count = 0
        self.add_data()
        
        # returning the root widget
        return self.wid
        
    def add_data(self):
        self.plotData1.add_coord(self.count, math.atan(self.count/180.0*math.pi))
        self.plotData2.add_coord(self.count, math.cos(self.count/180.0*math.pi))
        self.plotData3.add_coord(self.count, math.sin(self.count/180.0*math.pi))
        self.svgplot.render()
        self.count+=1
        Timer(0.01,self.add_data).start() 


if __name__ == "__main__":
    start(MyApp)
