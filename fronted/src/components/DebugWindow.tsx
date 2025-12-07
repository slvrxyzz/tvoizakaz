'use client'

interface DebugWindowProps {
  data: any
}

export default function DebugWindow({ data }: DebugWindowProps) {
  return (
    <div className="debug-window" style={{ display: 'none' }}>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}





