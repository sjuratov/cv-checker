/**
 * Tab Navigation Component
 * Accessible tab navigation for analysis results
 */

interface Tab {
  id: string;
  label: string;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export function TabNavigation({ tabs, activeTab, onTabChange }: TabNavigationProps) {
  const handleKeyDown = (e: React.KeyboardEvent, tabId: string) => {
    const currentIndex = tabs.findIndex((t) => t.id === activeTab);
    let nextIndex = currentIndex;

    switch (e.key) {
      case 'ArrowLeft':
        e.preventDefault();
        nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
        onTabChange(tabs[nextIndex].id);
        break;
      case 'ArrowRight':
        e.preventDefault();
        nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
        onTabChange(tabs[nextIndex].id);
        break;
      case 'Home':
        e.preventDefault();
        onTabChange(tabs[0].id);
        break;
      case 'End':
        e.preventDefault();
        onTabChange(tabs[tabs.length - 1].id);
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        onTabChange(tabId);
        break;
    }
  };

  return (
    <div className="tab-navigation" role="tablist" aria-label="Analysis sections">
      {tabs.map((tab, index) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            aria-controls={`tabpanel-${tab.id}`}
            id={`tab-${tab.id}`}
            tabIndex={isActive ? 0 : -1}
            className={`tab-button ${isActive ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, tab.id)}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
