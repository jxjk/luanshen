/**
 * PDF Export Service - English Version to Avoid Chinese Font Issues
 */

import jsPDF from 'jspdf'

export interface OptimizationResultPDFData {
  result: {
    speed: number
    feed: number
    cut_depth: number
    cut_width: number
    cutting_speed: number
    feed_per_tooth: number
    bottom_roughness: number
    side_roughness: number
    power: number
    torque: number
    feed_force: number
    material_removal_rate: number
    tool_life: number
    fitness: number
  }
  material?: {
    id: string
    name: string
    rm_min: number
    rm_max: number
    kc11: number
    mc: number
  }
  tool?: {
    id: number
    name: string
    type: string
    zhiJing: number
    chiShu: number
    vc_max: number
    fz_max: number
    ap_max: number
    daoJianR: number
  }
  machine?: {
    id: string
    name: string
    type: string
    pw_max: number
    rp_max: number
    tnm_max: number
    xiaoLv: number
    f_max: number
  }
  strategy?: {
    id: string
    name: string
    type: string
    rx_min: number
    rz_min: number
    lft_min: number
    ae: number
  }
  constraints?: Array<{
    name: string
    value: number
    max: number
    unit: string
    percentage: number
    variant: string
  }>
}

class PDFService {
  static generateOptimizationReport(data: OptimizationResultPDFData): void {
    const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const margin = 20
    const contentWidth = pageWidth - 2 * margin
    let yPosition = margin
    
    // Title
    pdf.setFontSize(24)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Process Parameter Optimization Report', pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 15
    
    // Date
    pdf.setFontSize(10)
    pdf.setFont('helvetica', 'normal')
    const date = new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
    pdf.text(`Generated: ${date}`, pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 10
    
    // Separator
    pdf.setDrawColor(200, 200, 200)
    pdf.line(margin, yPosition, pageWidth - margin, yPosition)
    yPosition += 15

    // Description
    pdf.setFontSize(11)
    pdf.setFont('helvetica', 'normal')
    pdf.setTextColor(80, 80, 80)
    
    const machiningType = data.strategy?.type || 'Unknown'
    const toolDiameter = data.tool?.zhiJing || 0
    const materialName = data.material?.name || 'Unknown'
    
    const description = `This report is based on Microbial Genetic Algorithm (MGA) for ${machiningType} optimization.`
    const description2 = `For ${materialName} material, using Φ${toolDiameter}mm tool,`
    const description3 = `maximizing material removal rate while satisfying tool life, power, torque, and surface roughness constraints.`
    
    pdf.text(description, margin, yPosition)
    yPosition += 6
    pdf.text(description2, margin, yPosition)
    yPosition += 6
    pdf.text(description3, margin, yPosition)
    yPosition += 12
    pdf.setTextColor(0, 0, 0)

    // Results Summary
    pdf.setFontSize(16)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Optimization Results Summary', margin, yPosition)
    yPosition += 8
    
    pdf.setFontSize(12)
    pdf.setFont('helvetica', 'normal')
    
    const coreParams = [
      { label: 'Speed', value: `${data.result.speed.toFixed(0)} r/min` },
      { label: 'Feed Rate', value: `${data.result.feed.toFixed(0)} mm/min` },
      { label: 'Cut Depth', value: `${data.result.cut_depth.toFixed(2)} mm` },
      { label: 'Cut Width', value: `${data.result.cut_width.toFixed(2)} mm` },
      { label: 'Cutting Speed', value: `${data.result.cutting_speed.toFixed(2)} m/min` },
      { label: 'Feed per Tooth', value: `${data.result.feed_per_tooth.toFixed(4)} mm` },
    ]
    
    const cellWidth = contentWidth / 3
    const cellHeight = 12
    
    pdf.setDrawColor(220, 220, 220)
    for (let i = 0; i < coreParams.length; i++) {
      const col = i % 3
      const row = Math.floor(i / 3)
      const x = margin + col * cellWidth
      const y = yPosition + row * cellHeight
      
      pdf.rect(x, y, cellWidth, cellHeight)
      
      pdf.setFontSize(10)
      pdf.setTextColor(100, 100, 100)
      pdf.text(coreParams[i].label, x + 3, y + 5)
      
      pdf.setFontSize(11)
      pdf.setTextColor(0, 0, 0)
      pdf.setFont('helvetica', 'bold')
      pdf.text(coreParams[i].value, x + 3, y + 9)
      pdf.setFont('helvetica', 'normal')
    }
    
    yPosition += cellHeight * 2 + 15
    
    // Material Removal Rate
    pdf.setFillColor(220, 240, 220)
    pdf.rect(margin, yPosition, contentWidth, 20, 'F')
    
    pdf.setFontSize(14)
    pdf.setFont('helvetica', 'bold')
    pdf.setTextColor(34, 139, 34)
    pdf.text(`Material Removal Rate: ${data.result.material_removal_rate.toFixed(2)} cm³/min`, margin + 5, yPosition + 13)
    pdf.setTextColor(0, 0, 0)
    yPosition += 25
    
    // Configuration
    pdf.setFontSize(16)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Processing Parameters Configuration', margin, yPosition)
    yPosition += 10
    
    if (data.material) {
      this.drawSectionBox(pdf, 'Material', margin, yPosition, contentWidth)
      yPosition += 8
      pdf.setFontSize(11)
      pdf.text(`Name: ${data.material.name}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Material Group: ${data.material.id}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Tensile Strength: ${data.material.rm_min}-${data.material.rm_max} MPa`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Specific Cutting Force: ${data.material.kc11} N/mm²`, margin + 5, yPosition)
      yPosition += 10
    }
    
    if (data.tool) {
      this.drawSectionBox(pdf, 'Tool', margin, yPosition, contentWidth)
      yPosition += 8
      pdf.setFontSize(11)
      pdf.text(`Name: ${data.tool.name}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Type: ${data.tool.type}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Diameter: Φ${data.tool.zhiJing} mm`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Teeth: ${data.tool.chiShu}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Corner Radius: R${data.tool.daoJianR} mm`, margin + 5, yPosition)
      yPosition += 10
    }
    
    if (data.machine) {
      this.drawSectionBox(pdf, 'Machine', margin, yPosition, contentWidth)
      yPosition += 8
      pdf.setFontSize(11)
      pdf.text(`Name: ${data.machine.name}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Type: ${data.machine.type}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Power: ${data.machine.pw_max} Kw`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Max Speed: ${data.machine.rp_max} r/min`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Max Torque: ${data.machine.tnm_max} Nm`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Efficiency: ${(data.machine.xiaoLv * 100).toFixed(0)}%`, margin + 5, yPosition)
      yPosition += 10
    }
    
    if (data.strategy) {
      this.drawSectionBox(pdf, 'Strategy', margin, yPosition, contentWidth)
      yPosition += 8
      pdf.setFontSize(11)
      pdf.text(`Name: ${data.strategy.name}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Type: ${data.strategy.type}`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Min Tool Life: ${data.strategy.lft_min} min`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Cut Width: ${data.strategy.ae} mm`, margin + 5, yPosition)
      yPosition += 6
      pdf.text(`Side Roughness: Ra ${data.strategy.rx_min} μm`, margin + 5, yPosition)
      yPosition += 10
    }
    
    if (yPosition > pageHeight - 60) {
      pdf.addPage()
      yPosition = margin
    }
    
    // Performance Metrics
    pdf.setFontSize(16)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Performance Metrics', margin, yPosition)
    yPosition += 10
    
    const performanceMetrics = [
      { label: 'Power', value: `${data.result.power.toFixed(2)} Kw` },
      { label: 'Torque', value: `${data.result.torque.toFixed(2)} Nm` },
      { label: 'Feed Force', value: `${data.result.feed_force.toFixed(2)} N` },
      { label: 'Tool Life', value: `${data.result.tool_life.toFixed(2)} min` },
      { label: 'Bottom Roughness', value: `Ra ${data.result.bottom_roughness.toFixed(2)} μm` },
      { label: 'Side Roughness', value: `Ra ${data.result.side_roughness.toFixed(2)} μm` },
    ]
    
    performanceMetrics.forEach((metric, index) => {
      if (index % 2 === 0 && yPosition > pageHeight - 30) {
        pdf.addPage()
        yPosition = margin
      }
      
      const col = index % 2
      const x = margin + col * (contentWidth / 2)
      
      pdf.setFontSize(10)
      pdf.setTextColor(100, 100, 100)
      pdf.text(`${metric.label}:`, x, yPosition)
      
      pdf.setFontSize(11)
      pdf.setTextColor(0, 0, 0)
      pdf.setFont('helvetica', 'bold')
      pdf.text(metric.value, x + 35, yPosition)
      pdf.setFont('helvetica', 'normal')
      
      if (col === 1) {
        yPosition += 8
      }
    })
    
    yPosition += 10
    
    // Constraints
    if (data.constraints && data.constraints.length > 0) {
      if (yPosition > pageHeight - 80) {
        pdf.addPage()
        yPosition = margin
      }
      
      pdf.setFontSize(16)
      pdf.setFont('helvetica', 'bold')
      pdf.text('Constraint Usage', margin, yPosition)
      yPosition += 10
      
      data.constraints.forEach((constraint) => {
        if (yPosition > pageHeight - 20) {
          pdf.addPage()
          yPosition = margin
        }
        
        pdf.setFillColor(240, 240, 240)
        pdf.rect(margin + 45, yPosition - 4, contentWidth - 45, 8, 'F')
        
        const barWidth = (contentWidth - 45) * (constraint.percentage / 100)
        let fillColor = [76, 175, 80]
        if (constraint.percentage > 80) fillColor = [255, 152, 0]
        if (constraint.percentage > 95) fillColor = [244, 67, 54]
        
        pdf.setFillColor(fillColor[0], fillColor[1], fillColor[2])
        pdf.rect(margin + 45, yPosition - 4, barWidth, 8, 'F')
        
        pdf.setFontSize(10)
        pdf.setTextColor(0, 0, 0)
        pdf.setFont('helvetica', 'normal')
        pdf.text(
          `${constraint.name}: ${constraint.value.toFixed(2)} / ${constraint.max} ${constraint.unit} (${constraint.percentage.toFixed(0)}%)`,
          margin,
          yPosition + 2
        )
        
        yPosition += 12
      })
    }
    
    // Recommendations
    if (yPosition > pageHeight - 80) {
      pdf.addPage()
      yPosition = margin
    }
    
    pdf.setFontSize(16)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Optimization Recommendations', margin, yPosition)
    yPosition += 10
    
    const suggestions: string[] = []
    
    if (data.constraints) {
      const powerConstraint = data.constraints.find(c => c.name === 'Power')
      if (powerConstraint && powerConstraint.percentage > 90) {
        suggestions.push('• Power usage is high. Monitor machine load to avoid overload.')
      }
      
      const torqueConstraint = data.constraints.find(c => c.name === 'Torque')
      if (torqueConstraint && torqueConstraint.percentage > 90) {
        suggestions.push('• Torque is near limit. Consider reducing cut depth or feed per tooth.')
      }
      
      const toolLifeConstraint = data.constraints.find(c => c.name === 'Tool Life')
      if (toolLifeConstraint && toolLifeConstraint.value < toolLifeConstraint.max * 0.5) {
        suggestions.push('• Tool life is short. Optimize cooling conditions or reduce cutting parameters.')
      }
    }
    
    if (data.result.material_removal_rate < 50) {
      suggestions.push('• Material removal rate is low. Consider optimizing parameters for better efficiency.')
    } else if (data.result.material_removal_rate > 200) {
      suggestions.push('• Material removal rate is high. Monitor tool wear and workpiece quality.')
    }
    
    if (suggestions.length === 0) {
      suggestions.push('• Optimization parameters are reasonable. Proceed with machining.')
      suggestions.push('• Monitor cutting status and tool wear during machining.')
      suggestions.push('• Adjust parameters if any abnormalities occur.')
    }
    
    pdf.setFontSize(11)
    pdf.setFont('helvetica', 'normal')
    suggestions.forEach((suggestion) => {
      if (yPosition > pageHeight - 15) {
        pdf.addPage()
        yPosition = margin
      }
      pdf.text(suggestion, margin, yPosition)
      yPosition += 7
    })
    
    yPosition += 10
    
    // Disclaimer
    if (yPosition > pageHeight - 40) {
      pdf.addPage()
      yPosition = margin
    }
    
    pdf.setFontSize(9)
    pdf.setFont('helvetica', 'italic')
    pdf.setTextColor(150, 150, 150)
    
    const disclaimer = 'Disclaimer: This report is for reference only. Actual machining parameters should be adjusted'
    const disclaimer2 = 'according to specific conditions, machine performance, tool status, and workpiece quality requirements.'
    const disclaimer3 = 'Trial cutting verification is recommended before mass production.'
    
    pdf.text(disclaimer, margin, yPosition)
    yPosition += 5
    pdf.text(disclaimer2, margin, yPosition)
    yPosition += 5
    pdf.text(disclaimer3, margin, yPosition)
    
    pdf.setTextColor(0, 0, 0)
    pdf.setFont('helvetica', 'normal')
    
    yPosition += 15

    // Footer
    const totalPages = pdf.getNumberOfPages()
    for (let i = 1; i <= totalPages; i++) {
      pdf.setPage(i)
      pdf.setFontSize(9)
      pdf.setTextColor(150, 150, 150)
      pdf.text(`Page ${i} of ${totalPages}`, pageWidth / 2, pageHeight - 10, { align: 'center' })
      pdf.text('Process Parameter Optimization System v1.0.0', margin, pageHeight - 10)
      pdf.text(`Generated: ${date}`, pageWidth - margin, pageHeight - 10, { align: 'right' })
    }
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
    pdf.save(`Optimization_Report_${timestamp}.pdf`)
  }
  
  private static drawSectionBox(pdf: jsPDF, title: string, x: number, y: number, width: number): void {
    pdf.setFillColor(245, 245, 245)
    pdf.rect(x, y, width, 22, 'F')
    pdf.setDrawColor(220, 220, 220)
    pdf.rect(x, y, width, 22)
    pdf.setFontSize(12)
    pdf.setFont('helvetica', 'bold')
    pdf.setTextColor(70, 70, 70)
    pdf.text(title, x + 5, y + 14)
    pdf.setTextColor(0, 0, 0)
  }
}

export default PDFService