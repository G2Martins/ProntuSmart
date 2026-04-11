import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GestaoAreas } from './gestao-areas';

describe('GestaoAreas', () => {
    let component: GestaoAreas;
    let fixture: ComponentFixture<GestaoAreas>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [GestaoAreas],
        }).compileComponents();

        fixture = TestBed.createComponent(GestaoAreas);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
