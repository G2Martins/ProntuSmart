import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvaliacaoFuncional } from './avaliacao-funcional';

describe('AvaliacaoFuncional', () => {
    let component: AvaliacaoFuncional;
    let fixture: ComponentFixture<AvaliacaoFuncional>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [AvaliacaoFuncional],
        }).compileComponents();

        fixture = TestBed.createComponent(AvaliacaoFuncional);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
