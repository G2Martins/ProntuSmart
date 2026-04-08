import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InsercaoMetaSmart } from './insercao-meta-smart';

describe('InsercaoMetaSmart', () => {
    let component: InsercaoMetaSmart;
    let fixture: ComponentFixture<InsercaoMetaSmart>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [InsercaoMetaSmart],
        }).compileComponents();

        fixture = TestBed.createComponent(InsercaoMetaSmart);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
