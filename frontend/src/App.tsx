import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/layout/Navbar'
import Sidebar from './components/layout/Sidebar'
import OptimizationPage from './pages/OptimizationPage'
import MaterialsPage from './pages/MaterialsPage'
import ToolsPage from './pages/ToolsPage'
import MachinesPage from './pages/MachinesPage'
import StrategiesPage from './pages/StrategiesPage'
import HistoryPage from './pages/HistoryPage'
import WorkshopPage from './pages/WorkshopPage'
import DeviceMonitorPage from './pages/DeviceMonitorPage'
import DigitalTwinPage from './pages/DigitalTwinPage'
import KnowledgePage from './pages/KnowledgePage'
import QualityPage from './pages/QualityPage'
import ReportsPage from './pages/ReportsPage'
import FixturesPage from './pages/FixturesPage'
import NCSimulationPage from './pages/NCSimulationPage'
import EnergyAnalysisPage from './pages/EnergyAnalysisPage'
import ToolLifePage from './pages/ToolLifePage'
import './App.css'

function App() {
  return (
    <div className="app">
      <Navbar />
      <div className="d-flex">
        <Sidebar />
        <main className="main-content flex-grow-1">
          <Routes>
            {/* 默认路由重定向到车间视图 */}
            <Route path="/" element={<Navigate to="/workshop" replace />} />

            {/* 主菜单 */}
            <Route path="/workshop" element={<WorkshopPage />} />
            <Route path="/optimization" element={<OptimizationPage />} />
            <Route path="/digital-twin" element={<DigitalTwinPage />} />
            <Route path="/quality" element={<QualityPage />} />

            {/* 高级功能 */}
            <Route path="/nc-simulation" element={<NCSimulationPage />} />
            <Route path="/energy-analysis" element={<EnergyAnalysisPage />} />
            <Route path="/tool-life" element={<ToolLifePage />} />

            {/* 资源管理 */}
            <Route path="/materials" element={<MaterialsPage />} />
            <Route path="/tools" element={<ToolsPage />} />
            <Route path="/machines" element={<MachinesPage />} />
            <Route path="/strategies" element={<StrategiesPage />} />
            <Route path="/fixtures" element={<FixturesPage />} />

            {/* 知识与分析 */}
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/reports" element={<ReportsPage />} />

            {/* 设备监控 */}
            <Route path="/monitoring/:deviceId" element={<DeviceMonitorPage />} />

            {/* 404 路由 */}
            <Route path="*" element={<Navigate to="/workshop" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App