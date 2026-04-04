import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GestaoIndicadores } from './gestao-indicadores';

describe('GestaoIndicadores', () => {
    let component: GestaoIndicadores;
    let fixture: ComponentFixture<GestaoIndicadores>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [GestaoIndicadores],
        }).compileComponents();

        fixture = TestBed.createComponent(GestaoIndicadores);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
