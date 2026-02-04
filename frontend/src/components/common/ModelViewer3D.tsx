import React, { useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

interface ModelViewer3DProps {
  modelType?: 'machine' | 'tool' | 'fixture'
  autoRotate?: boolean
}

// 简单的机床模型组件
const MachineModel: React.FC = () => {
  return (
    <group>
      {/* 底座 */}
      <mesh position={[0, -1, 0]}>
        <boxGeometry args={[4, 0.5, 3]} />
        <meshStandardMaterial color="#4a5568" />
      </mesh>
      {/* 立柱 */}
      <mesh position={[1.5, 1.5, 0]}>
        <boxGeometry args={[0.8, 3, 0.8]} />
        <meshStandardMaterial color="#2d3748" />
      </mesh>
      {/* 主轴箱 */}
      <mesh position={[1.5, 3.2, 0]}>
        <boxGeometry args={[1, 0.8, 1]} />
        <meshStandardMaterial color="#1a202c" />
      </mesh>
      {/* 主轴 */}
      <mesh position={[1.5, 2.8, 0.8]}>
        <cylinderGeometry args={[0.15, 0.15, 0.8, 32]} />
        <meshStandardMaterial color="#718096" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* 工作台 */}
      <mesh position={[0, -0.7, 0]}>
        <boxGeometry args={[2.5, 0.1, 2]} />
        <meshStandardMaterial color="#e2e8f0" metalness={0.3} roughness={0.7} />
      </mesh>
      {/* 工件 */}
      <mesh position={[0, -0.5, 0]}>
        <boxGeometry args={[1, 0.5, 1]} />
        <meshStandardMaterial color="#ed8936" />
      </mesh>
    </group>
  )
}

// 简单的刀具模型组件
const ToolModel: React.FC = () => {
  return (
    <group rotation={[0, 0, -Math.PI / 2]}>
      {/* 刀柄 */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.2, 0.2, 2, 32]} />
        <meshStandardMaterial color="#2d3748" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* 刀体 */}
      <mesh position={[0, 1.5, 0]}>
        <cylinderGeometry args={[0.15, 0.12, 1, 32]} />
        <meshStandardMaterial color="#718096" metalness={0.9} roughness={0.1} />
      </mesh>
      {/* 刀片 */}
      <mesh position={[0, 2.1, 0]}>
        <boxGeometry args={[0.3, 0.2, 0.05]} />
        <meshStandardMaterial color="#f6ad55" metalness={0.7} roughness={0.3} />
      </mesh>
      <mesh position={[0, 2.1, 0.05]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[0.3, 0.2, 0.05]} />
        <meshStandardMaterial color="#f6ad55" metalness={0.7} roughness={0.3} />
      </mesh>
    </group>
  )
}

// 简单的夹具模型组件
const FixtureModel: React.FC = () => {
  return (
    <group>
      {/* 虎钳底座 */}
      <mesh position={[0, -0.3, 0]}>
        <boxGeometry args={[1.5, 0.3, 0.8]} />
        <meshStandardMaterial color="#4a5568" metalness={0.6} roughness={0.4} />
      </mesh>
      {/* 固定钳口 */}
      <mesh position={[-0.5, 0.3, 0]}>
        <boxGeometry args={[0.2, 0.6, 0.6]} />
        <meshStandardMaterial color="#2d3748" metalness={0.7} roughness={0.3} />
      </mesh>
      {/* 活动钳口 */}
      <mesh position={[0.5, 0.3, 0]}>
        <boxGeometry args={[0.2, 0.6, 0.6]} />
        <meshStandardMaterial color="#2d3748" metalness={0.7} roughness={0.3} />
      </mesh>
      {/* 工件 */}
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[0.6, 0.4, 0.4]} />
        <meshStandardMaterial color="#48bb78" />
      </mesh>
      {/* 螺杆 */}
      <mesh position={[0, 0, -0.35]}>
        <cylinderGeometry args={[0.05, 0.05, 1.5, 16]} />
        <meshStandardMaterial color="#a0aec0" metalness={0.8} roughness={0.2} />
      </mesh>
    </group>
  )
}

const ModelViewer3D: React.FC<ModelViewer3DProps> = ({ 
  modelType = 'machine',
  autoRotate = true 
}) => {
  const [isRotating, setIsRotating] = useState(autoRotate)

  return (
    <div style={{ width: '100%', height: '400px', background: '#1a202c', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas
        camera={{ position: [5, 4, 5], fov: 50 }}
      >
        {/* 环境光 */}
        <ambientLight intensity={0.4} />
        
        {/* 主光源 */}
        <directionalLight
          position={[5, 10, 5]}
          intensity={1}
        />
        
        {/* 补光 */}
        <pointLight position={[-5, 5, -5]} intensity={0.5} />
        
        {/* 坐标轴辅助 */}
        <primitive object={new THREE.AxesHelper(2)} />
        
        {/* 模型 */}
        {modelType === 'machine' && <MachineModel />}
        {modelType === 'tool' && <ToolModel />}
        {modelType === 'fixture' && <FixtureModel />}
        
        {/* 轨道控制 */}
        <OrbitControls 
          autoRotate={isRotating}
          autoRotateSpeed={2}
          enablePan={true}
          enableZoom={true}
          minDistance={2}
          maxDistance={15}
        />
      </Canvas>
      
      {/* 控制面板 */}
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '10px',
        background: 'rgba(0, 0, 0, 0.7)',
        padding: '10px',
        borderRadius: '4px',
        color: 'white'
      }}>
        <button 
          onClick={() => setIsRotating(!isRotating)}
          style={{
            background: isRotating ? '#48bb78' : '#e53e3e',
            border: 'none',
            color: 'white',
            padding: '5px 10px',
            borderRadius: '4px',
            cursor: 'pointer',
            marginRight: '5px'
          }}
        >
          {isRotating ? '⏸ 暂停' : '▶ 旋转'}
        </button>
        <small style={{ marginLeft: '10px', color: '#a0aec0' }}>
          {modelType === 'machine' ? '机床模型' : 
           modelType === 'tool' ? '刀具模型' : '夹具模型'}
        </small>
      </div>
    </div>
  )
}

export default ModelViewer3D