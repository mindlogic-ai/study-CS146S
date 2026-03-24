import { Notes } from './components/Notes';
import { ActionItems } from './components/ActionItems';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Notes & Action Items
          </h1>
          <p className="text-gray-600">
            Stay organized and productive
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-7xl mx-auto">
          <div className="bg-white/50 backdrop-blur-sm rounded-xl shadow-lg p-6 h-[calc(100vh-16rem)] overflow-hidden">
            <Notes />
          </div>

          <div className="bg-white/50 backdrop-blur-sm rounded-xl shadow-lg p-6 h-[calc(100vh-16rem)] overflow-hidden">
            <ActionItems />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
