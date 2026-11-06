import './SidePanel.css';
import { sidebarLinks } from './sidePanelLinks'
import { memo } from 'react';
import { NavLink } from 'react-router-dom';
const SidePanel = () => {
    return (
        <aside className="side-panel">
            <h3 className="side-panel__title">SportUA</h3>
            <nav className="side-panel__navigation">
                {sidebarLinks.map((link) => (
                    <NavLink 
                        key={`g-${link.id}`} 
                        className={`side-panel__btn`}
                        to={link.path}
                    >
                        {link.labelKey}
                    </NavLink> 
    

                ))}
            </nav>
        </aside>
    );
};

export default memo(SidePanel);